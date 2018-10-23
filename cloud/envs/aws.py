from cloud.envs import env
from cloud.envs import registry
from cloud.envs import utils


@registry.register("aws")
class AWSInstance(env.Instance):

  def __init__(self, config, **kwargs):
    super().__init__(**kwargs)
    self.access_key = config["access_key"]
    self.secret_key = config["secret_key"]

  @property
  def driver(self):
    if getattr(self, '_driver', None) is None:
      self._driver = get_driver(Provider.EC2)(self.access_key, self.secret_key)
    return self._driver

  @property
  def name(self):
    if getattr(self, '_name', None) is None:
      self._name = utils.call(["hostname"])[1].strip()
    return self._name