from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

from cloud.envs import env, registry, utils


@registry.register("azure")
class AzureInstance(env.Instance):

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.application_id = config["application_id"]
        self.subscription_id = config["subscription_id"]
        self.tenant_id = config["tenant_id"]
        self.key = config["key"]

    @property
    def driver(self):
        if getattr(self, '_driver', None) is None:
            self._driver = get_driver(Provider.AZURE_ARM)(tenant_id=self.tenant_id,
                                                          subscription_id=self.subscription_id,
                                                          key=self.application_id,
                                                          secret=self.key)
        return self._driver

    @property
    def name(self):
        if getattr(self, '_name', None) is None:
            self._name = utils.call(["hostname"])[1].strip()
        return self._name
