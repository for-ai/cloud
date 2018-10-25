import os

from cloud.envs import env
from cloud.envs import registry
from cloud.envs import utils

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


@registry.register("aws")
class AWSInstance(env.Instance):

  def __init__(self, config, **kwargs):
    super().__init__(**kwargs)
    # read from env first

    # support env variables required by AWS
    # https://docs.aws.amazon.com/cli/latest/userguide/cli-environment.html
    self.access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    # fallback to config values otherwise
    if self.access_key is None:
      self.access_key = config["access_key"]

    if self.secret_key is None:
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