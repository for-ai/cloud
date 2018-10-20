import logging
import traceback

from cloud.envs import utils


class Instance(object):

  def __init__(self):
    super().__init__()
    self.resource_managers = []

  def __del__(self):
    for rm in self.resource_managers:
      del rm

  @property
  def name(self):
    raise NotImplementedError

  def down(self):
    raise NotImplementedError

  def delete(self, confirm=True):
    raise NotImplementedError


class Resource(object):

  def __init__(self):
    super().__init__()

  @property
  def name(self):
    raise NotImplementedError

  @property
  def down_cmd(self):
    raise NotImplementedError

  def down(self):
    utils.try_call(self.down_cmd)


class ResourceManager(object):

  def __init__(self, instance, resource_cls):
    super().__init__()
    self.instance = instance
    self.resource_cls = resource_cls
    self.resources = []

  def __del__(self):
    for r in self.resources:
      try:
        r.down()
      except Exception as e:
        logging.error("Failed to shutdown resource: %s" % r)
        logging.error(traceback.format_exc())

  @property
  def name(self):
    raise NotImplementedError

  @property
  def up_cmd(self):
    raise NotImplementedError

  @property
  def preemptible_flag(self):
    return ""

  def up(self, preemptible=True):
    cmd = self.up_cmd
    if preemptible:
      if callable(cmd):
        cmd = lambda c=cmd: c() + [self.preemptible_flag]
    utils.try_call(cmd)
