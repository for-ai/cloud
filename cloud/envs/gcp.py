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

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    # Check for dependencies
    try:
      utils.call(["gcloud", "--version"])
    except:
      raise Exception("Missing commandline utility: gcloud")

    self.tpu = TPUManager(self)
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
    return (details["state"] in ["READY"] and details["health"] == "HEALTHY")

  @property
  def in_use(self):
    details = self.details
    return (details["state"] in ["RUNNING"] and details["health"] == "HEALTHY")

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

  def __init__(self, instance):
    super().__init__(instance, TPU)
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
    self.resources.extend(tpus)

  def new_name(self, length=5):
    while True:
      name = random.sample(string.ascii_lowercase, length)
      name = self.instance.name + "-" + ''.join(name)
      if name not in self.names:
        return name

  def new_ip(self):
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

    return self.up(preemptible)

  def up(self, preemptible=True):

    def cmd():
      self.tmp_name = self.new_name()
      self.tmp_ip = self.new_ip()
      logging.info(f"Trying to acquire TPU with name: "
                   "{self.tmp_name} ip: {self.tmp_ip}")
      cmd = [
          "gcloud", "alpha", "compute", "tpus", "create", self.tmp_name,
          f"--range=10.0.{self.tmp_ip}.0/29", "--version=1.11",
          "--network=default"
      ]
      if preemptible:
        cmd += ["--preemptible"]
      return cmd

    utils.try_call(cmd)
    tpu = TPU(name=self.tmp_name)
    self.resources.append(tpu)

    return tpu
