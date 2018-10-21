import logging
import traceback

from cloud.envs import utils


class Resource(object):

  def __init__(self, manager=None):
    super().__init__()
    self.manager = manager

  @property
  def name(self):
    raise NotImplementedError

  @property
  def down_cmd(self):
    raise NotImplementedError

  @property
  def delete_cmd(self):
    raise NotImplementedError

  @property
  def usable(self):
    return True

  def down(self):
    utils.try_call(self.down_cmd)

  def delete(self):
    utils.try_call(self.delete_cmd)
    if self.manager:
      self.manager.remove(self)


class Instance(Resource):

  def __init__(self):
    super().__init__()
    self.resource_managers = []

  def __del__(self):
    for rm in self.resource_managers:
      del rm


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

  def __get__(self, idx):
    return self.resources[idx]

  @property
  def name(self):
    raise NotImplementedError

  @property
  def up_cmd(self):
    raise NotImplementedError

  @property
  def preemptible_flag(self):
    return ""

  def add(self, *args, **kwargs):
    if len(args) == 1:
      arg = args[0]
      if isinstance(arg, self.resource_cls):
        self.resources += [arg]
        return arg

    raise NotImplementedError

  def remove(self, *args, **kwargs):
    if len(args) == 1:
      arg = args[0]
      if isinstance(arg, self.resource_cls):
        self.resources.remove(arg)
        return

    raise NotImplementedError

  def up(self, preemptible=True):
    cmd = self.up_cmd
    if preemptible:
      if callable(cmd):
        cmd = lambda c=cmd: c() + [self.preemptible_flag]
    utils.try_call(cmd)
