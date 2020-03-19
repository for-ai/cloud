import os

import requests
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

from cloud.envs import env, registry, utils


@registry.register("aws")
class AWSInstance(env.Instance):

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.access_key = config["access_key"]
        self.secret_key = config["secret_key"]
        self.region = config["region"]

    @property
    def driver(self):
        if getattr(self, '_driver', None) is None:
            self._driver = get_driver(Provider.EC2)(self.access_key, self.secret_key, region=self.region)
        return self._driver

    @property
    def name(self):
        if getattr(self, '_name', None) is None:
            # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html
            r = requests.get("http://169.254.169.254/latest/meta-data/instance-id")
            self._name = r.text
        return self._name
