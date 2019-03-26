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

logger = logging.getLogger(__name__)


@registry.register("gcp")
class GCPInstance(env.Instance):

  def __init__(self, collect_existing_tpus=True, **kwargs):
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
    self.ip = details.get("ipAddress")
    self.preemptible = details.get("preemptible") == "true"

  @property
  def name(self):
    return self._name

  @property
  def details(self):
    _, r, _ = utils.call(
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
  def still_exists(self):
    return self.name in self.manager.get_all_tpu_names()

  @property
  def usable(self):
    details = self.details
    if not self.still_exists:
      self.manager.remove(self)
      return False
    is_running = details.get("state") in ["READY", "RUNNING"]
    is_healthy = details.get("health") in ["HEALTHY", None]
    return is_running and is_healthy

  def up(self, background=False):
    cmd = ["gcloud", "alpha", "compute", "tpus", "start", self.name]
    if background:
      cmd += ["--async"]

    utils.try_call(cmd)

  def down(self, background=True):
    cmd = ["gcloud", "alpha", "compute", "tpus", "stop", self.name]
    if background:
      cmd += ["--async"]

    utils.try_call(cmd)

  def delete(self, background=True):
    super().delete(background=background)

    if not self.still_exists:
      return

    cmd = ["gcloud", "alpha", "compute", "tpus", "delete", self.name]
    if background:
      cmd += ["--async"]
    cmd += ["--quiet"]  # suppress user confirmation

    utils.try_call(cmd)


class TPUManager(env.ResourceManager):

  def __init__(self, instance):
    super().__init__(instance, TPU)
    try:
      import tensorflow as tf
      import re
      m = re.search(r'(\d+\.\d+)\.\d+', tf.__version__)
      self.tf_version = m.group(1)
    except:
      logger.warn("Unable to determine Tensorflow version. Assuming 1.12")
      self.tf_version = "1.12"
    self.refresh()

  @property
  def names(self):
    return [r.name for r in self.resources]

  @property
  def ips(self):
    return [r.ip for r in self.resources]

  def get_all_tpu_names(self):
    _, r, _ = utils.call(["gcloud", "alpha", "compute", "tpus", "list"])
    lines = r.split("\n")[1:]
    lines = filter(lambda l: l != "", lines)
    names = [l.split()[0] for l in lines]
    return filter(lambda n: self.instance.name in n, names)

  def refresh(self, background=True):
    self.collect_existing()
    self.clean(background=background)

  def collect_existing(self):
    names = self.get_all_tpu_names()
    existing_names = self.names
    new_tpus = [
        TPU(name=n, manager=self) for n in names if n not in existing_names
    ]

    for tpu in new_tpus:
      logger.info("Found TPU named {}".format(tpu.name))

    self.resources.extend(new_tpus)

  def clean(self, background=True):
    all_tpu_names = self.get_all_tpu_names()
    for tpu in self.resources:
      if tpu.name not in all_tpu_names:
        self.remove(tpu)
      elif not tpu.usable:
        tpu.delete(background=background)

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
        tpu = TPU(name=arg, manager=self)
        self.resources.append(tpu)
        return tpu
    return super().add(*args, **kwargs)

  def get(self, preemptible=True, name=None):
    for tpu in self.resources:
      if tpu.usable and not name:
        return tpu

      if tpu.name == name:
        return tpu

    return self.up(preemptible=preemptible, name=name)

  def _up(self, name, ip, preemptible, background):
    logger.info("Trying to acquire TPU with name: {} ip: {}".format(name, ip))
    cmd = [
        "gcloud", "alpha", "compute", "tpus", "create", name,
        "--range=10.0.{}.0/29".format(ip), "--version={}".format(
            self.tf_version), "--network=default"
    ]
    if preemptible:
      cmd += ["--preemptible"]
    if background:
      cmd += ["--async"]

    s, _, err = utils.call(cmd)
    if s == 0:
      return TPU(name=name)

    raise Exception(
        "Failed to create TPU with name: {} ip: {} error: \n{}".format(
            name, ip, err))

  def up(self, preemptible=True, background=False, attempts=5, name=None):
    if not name:
      name = self._new_name()
    for i in range(attempts):
      try:
        tpu = self._up(
            name,
            self._new_ip(),
            preemptible=preemptible,
            background=background)
        tpu.manager = self
        self.resources.append(tpu)
        return tpu
      except Exception as e:
        if i + 1 == attempts:
          raise e
        continue
