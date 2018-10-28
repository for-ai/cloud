import logging
import random
import re
import string
import subprocess
import requests
import numpy as np

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from cloud.envs import env
from cloud.envs import registry
from cloud.envs import utils


@registry.register("gcp")
class GCPInstance(env.Instance):

  def __init__(self, collect_existing_tpus=True, **kwargs):
    super().__init__(**kwargs)

    # Check for dependencies
    try:
      utils.call(["gcloud", "--version"])
    except:
      raise Exception("Missing commandline utility: gcloud")

    self.tpu = TPUManager(self, collect_existing=collect_existing_tpus)
    self.resource_managers = [self.tpu]

  @property
  def driver(self):
    if getattr(self, '_driver', None) is None:
      r = requests.get(
          "http://metadata.google.internal/computeMetadata/v1/project/project-id",
          headers={"Metadata-Flavor": "Google"})
      project_id = r.text
      self._driver = get_driver(Provider.GCE)("", "", project=project_id)
    return self._driver

  @property
  def name(self):
    if getattr(self, '_name', None) is None:
      self._name = utils.call(["hostname"])[1].strip()
    return self._name


class TPU(env.Resource):

  def __init__(self, name, manager=None):
    super().__init__(manager=manager)
    self._name = name
    details = self.details
    self.ip = details["ipAddress"]
    self.preemptible = details.get("preemptible") == "true"

  @property
  def name(self):
    return self._name

  @property
  def details(self):
    _, r = utils.call(
        ["gcloud", "alpha", "compute", "tpus", "describe", self.name])
    r = r.split("\n")
    details = dict()
    for line in r:
      v = line.split(": ")
      if len(v) != 2:
        continue
      k, v = v
      details[k.strip()] = v.strip()
    return details

  @property
  def usable(self):
    details = self.details
    return (details["state"] in ["READY", "RUNNING"] and
            details["health"] == "HEALTHY")

  def up(self, async=False):
    cmd = ["gcloud", "alpha", "compute", "tpus", "start", self.name]
    if async:
      cmd += ["--async"]

    utils.try_call(cmd)

  def down(self, async=False):
    cmd = ["gcloud", "alpha", "compute", "tpus", "stop", self.name]
    if async:
      cmd += ["--async"]

    utils.try_call(cmd)

  def delete(self, async=False):
    super().delete()

    cmd = ["gcloud", "alpha", "compute", "tpus", "delete", self.name]
    if async:
      cmd += ["--async"]
    cmd += ["--quiet"]  # suppress user confirmation

    utils.try_call(cmd)


class TPUManager(env.ResourceManager):

  def __init__(self, instance, collect_existing=True):
    super().__init__(instance, TPU)
    if collect_existing:
      self.collect_existing()

  @property
  def names(self):
    return [r.name for r in self.resources]

  @property
  def ips(self):
    return [r.ip for r in self.resources]

  def collect_existing(self):
    _, r = utils.call(["gcloud", "alpha", "compute", "tpus", "list"])
    lines = r.split("\n")[1:]
    lines = filter(lambda l: l != "", lines)
    names = [l.split()[0] for l in lines]
    names = filter(lambda n: self.instance.name in n, names)
    tpus = [TPU(name=n) for n in names]

    for tpu in tpus:
      logging.info(f"Found TPU named {tpu.name}")

    self.resources.extend(tpus)

  def clean(self, async=True):
    for tpu in self.resources:
      if tpu.details["health"] != "HEALTHY":
        tpu.delete(async=async)

  def _new_name(self, length=5):
    while True:
      name = random.sample(string.ascii_lowercase, length)
      name = self.instance.name + "-" + ''.join(name)
      if name not in self.names:
        return name

  def _new_ip(self):
    while True:
      ip = random.randint(1, 98)
      if ip not in self.ips:
        return ip

  def add(self, *args, **kwargs):
    if len(args) == 1:
      arg = args[0]
      if isinstance(arg, str):
        tpu = TPU(name=arg)
        self.resources.append(tpu)
        return tpu
    return super().add(*args, **kwargs)

  def get(self, preemptible=True):
    for tpu in self.resources:
      if tpu.usable:
        return tpu

    return self.up(preemptible=preemptible)

  def _up(self, name, ip, preemptible, async):
    logging.info(f"Trying to acquire TPU with name: {name} ip: {ip}")
    cmd = [
        "gcloud", "alpha", "compute", "tpus", "create", name,
        f"--range=10.0.{ip}.0/29", "--version=1.11", "--network=default"
    ]
    if preemptible:
      cmd += ["--preemptible"]
    if async:
      cmd += ["--async"]

    s, _ = utils.call(cmd)
    if s == 0:
      return TPU(name=name)

    raise Exception(f"Failed to create TPU with name: {name} ip: {ip}")

  def up(self, preemptible=True, async=False, attempts=5):
    for i in range(attempts):
      try:
        tpu = self._up(
            self._new_name(),
            self._new_ip(),
            preemptible=preemptible,
            async=async)
        tpu.manager = self
        self.resources.append(tpu)
        return tpu
      except Exception as e:
        if i + 1 == attempts:
          raise e
        continue
