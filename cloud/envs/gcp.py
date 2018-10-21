import random
import re
import string
import subprocess

import numpy as np

from cloud.envs import env
from cloud.envs import registry
from cloud.envs import utils


@registry.register("gcp")
class GCPInstance(env.Instance):

  def __init__(self):
    super().__init__()

    # Check for dependencies
    try:
      utils.call(["ctpu", "version"])
    except:
      raise Exception("Missing commandline utility: ctpu")
    try:
      utils.call(["gcloud", "--version"])
    except:
      raise Exception("Missing commandline utility: gcloud")

    self.tpu = TPUManager(self)
    self.resource_managers = [self.tpu]

  @property
  def name(self):
    return utils.call(["hostname"])[1].strip()

  def down(self):
    utils.try_call(["gcloud", "compute", "instances", "stop", self.name])

  def delete(self, confirm=True):
    while confirm:
      r = input("Are you sure you wish to delete this instance (y/[n]): ")

      if r == "y":
        break
      elif r in ["n", ""]:
        logging.info("Aborting deletion...")
        return

    utils.try_call(["gcloud", "compute", "instances", "delete", self.name])


class TPU(env.Resource):

  def __init__(self, name, manager=None):
    super().__init__(manager=manager)
    self._name = name
    details = self.details
    self.ip = details["ipAddress"]
    self.preemptible = details["preemptible"] == "true"

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
    return (details["state"] == "RUNNING" and details["health"] == "HEALTHY")

  @property
  def down_cmd(self):
    return ["gcloud", "alpha", "compute", "tpus", "stop", self.name]

  @property
  def delete_cmd(self):
    return ["gcloud", "alpha", "compute", "tpus", "delete", self.name]


class TPUManager(env.ResourceManager):

  def __init__(self, instance):
    super().__init__(instance, TPU)

  @property
  def up_cmd(self):

    def fn():
      self.tmp_name = self.new_name()
      self.tmp_ip = self.new_ip()
      return [
          "gcloud", "alpha", "compute", "tpus", "create", self.tmp_name,
          f"--range=10.0.{self.tmp_ip}.0/29", "--version=1.11",
          "--network=default"
      ]

    return fn

  @property
  def preemptible_flag(self):
    return "--preemptible"

  @property
  def names(self):
    return [r.name for r in self.resources]

  @property
  def ips(self):
    return [r.ip for r in self.resources]

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

  def up(self, preemptible=True):
    super().up(preemptible=preemptible)
    tpu = TPU(name=self.tmp_name)
    self.resources.append(tpu)

    return tpu
