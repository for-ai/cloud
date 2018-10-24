import libcloud
import toml

import cloud
from cloud import registry as reg
from cloud import Instance
from cloud.envs.utils import config_path


def connect():
  with open(config_path(), "r") as cf:
    config = toml.load(cf)
    provider = config.pop("provider").lower()
    cloud.instance = reg.retrieve(provider, config=config)


def down():
  cloud.instance.down()


def delete(confirm=True):
  cloud.instance.delete(confirm)
