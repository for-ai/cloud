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
  def usable(self):
    return True

  def down(self):
    raise NotImplementedError

  def delete(self, confirm=True):
    raise NotImplementedError


class Instance(Resource):

  def __init__(self, manager=None, **kwargs):
    super().__init__(manager=manager)
    self.resource_managers = []
    self.driver = driver
    self.node = filter(lambda n: n.name == self.name,
                       self.driver.list_nodes())[0]

  @property
  def driver(self):
    raise NotImplementedError

  def down(self):
    return self.node.shut_down()

  def delete(self, confirm=True):
    while confirm:
      r = input("Are you sure you wish to delete this instance (y/[n]): ")

      if r == "y":
        break
      elif r in ["n", ""]:
        logging.info("Aborting deletion...")
        return

    if self.manager:
      self.manager.remove(self)

    self.driver.destroy_node(self.node, destroy_boot_disk=True)


class ResourceManager(object):

  def __init__(self, instance, resource_cls):
    super().__init__()
    self.instance = instance
    self.resource_cls = resource_cls
    self.resources = []

  def __get__(self, idx):
    return self.resources[idx]

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

  def down(self):
    for r in self.resources:
      try:
        r.down()
      except Exception as e:
        logging.error("Failed to shutdown resource: %s" % r)
        logging.error(traceback.format_exc())

  def delete(self):
    for r in self.resources:
      try:
        r.delete()
      except Exception as e:
        logging.error("Failed to delete resource: %s" % r)
        logging.error(traceback.format_exc())
