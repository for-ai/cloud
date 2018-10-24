import libcloud
import toml

import cloud
from cloud import registry as reg
from cloud import Instance
from cloud.envs.utils import config_path


def connect(arg=None):
  if arg is None:
    with open(config_path(), "r") as cf:
      config = toml.load(cf)
      provider = config.pop("provider").lower()
      cloud.instance = reg.retrieve(provider, config=config)
  elif isinstance(arg, Instance):
    cloud.instance = arg
  else:
    raise Exception(f"Unknown input type: {type(arg)}."
                    " Please provide a string or Instance object, "
                    "or pass no arguments at all.")


def down():
  cloud.instance.down()


def delete(confirm=True):
  cloud.instance.delete(confirm)
