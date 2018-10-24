import libcloud
import toml

import cloud
from cloud import registry as reg
from cloud import Instance

instance = None


def connect(path):
  with open(path, "r") as cf:
    config = toml.loads(cf)
    provider = config.pop("provider").lower()
    global instance
    instance = reg.retrieve(provider, config=config)


def down():
  instance.down()


def delete(confirm=True):
  instance.delete(confirm)
