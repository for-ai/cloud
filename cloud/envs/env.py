import logging
import traceback
import sys
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

  def up(self, async=False):
    raise NotImplementedError

  def down(self, async=False):
    raise NotImplementedError

  def delete(self, async=False):
    if self.manager:
      self.manager.remove(self)


class Instance(Resource):

  def __init__(self, manager=None, **kwargs):
    super().__init__(manager=manager)
    self.resource_managers = []

  @property
  def driver(self):
    raise NotImplementedError

  @property
  def node(self):
    if getattr(self, '_node', None) is None:
      nodes = self.driver.list_nodes()
      if len(nodes) == 0:
        raise Exception(
            "list_nodes returned an empty list, did you set up your cloud permissions correctly?"
        )

      for n in nodes:
        if n.name == self.name:
          self._node = n

      # node not found
      if self._node is None:
        raise Exception(
            "current node could not be found - name: {} node_list: {}".format(
                self.name, nodes))

    return self._node

  def down(self, async=False, delete_resources=True):
    for rm in self.resource_managers:
      if delete_resources:
        rm.delete(async=async)
      else:
        rm.down(async=async)
    self.driver.ex_stop_node(self.node)

  def delete(self, async=False, confirm=True):
    while confirm:
      r = input("Are you sure you wish to delete this instance (y/[n]): ")

      if r == "y":
        break
      elif r in ["n", ""]:
        logging.info("Aborting deletion...")
        return

    super().delete(async=async)

    self.driver.destroy_node(self.node, destroy_boot_disk=True)


class ResourceManager(object):

  def __init__(self, instance, resource_cls):
    super().__init__()
    self.instance = instance
    self.resource_cls = resource_cls
    self.resources = []

  def __getitem__(self, idx):
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

  def up(self, async=False):
    raise NotImplementedError

  def down(self, async=False):
    for r in self.resources:
      try:
        r.down(async=async)
      except Exception as e:
        logging.error("Failed to shutdown resource: %s" % r)
        logging.error(traceback.format_exc())

  def delete(self, async=False):
    for r in self.resources:
      try:
        r.delete(async=async)
      except Exception as e:
        logging.error("Failed to delete resource: %s" % r)
        logging.error(traceback.format_exc())
