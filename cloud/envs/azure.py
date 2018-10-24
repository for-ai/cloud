from cloud.envs import env
from cloud.envs import registry
from cloud.envs import utils

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


@registry.register("azure")
class AzureInstance(env.Instance):

  def __init__(self, config, **kwargs):
    super().__init__(**kwargs)
    self.subscription_id = config["subscription_id"]
    self.key_file = config["key_file"]

  @property
  def driver(self):
    if getattr(self, '_driver', None) is None:
      self._driver = get_driver(Provider.AZURE)(
          subscription_id=self.subscription_id, key_file=self.key_file)
    return self._driver

  @property
  def name(self):
    if getattr(self, '_name', None) is None:
      self._name = utils.call(["hostname"])[1].strip()
    return self._name