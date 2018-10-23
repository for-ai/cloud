import libcloud
import toml

import cloud
from cloud import registry as reg
from cloud import Instance


def connect(arg=None):
  if arg is None:
    with open(path, "r") as cf:
      config = toml.loads(cf)
      provider = config.pop("provider").lower()
      cloud.instance = reg.retrieve(provider, config=config)
  elif isinstance(arg, str):
    cloud.instance = reg.retrieve(arg)
  elif isinstance(arg, Instance):
    cloud.instance = arg
  else:
    raise Exception(f"Unknown input type: {type(arg)}."
                    " Please provide a string or Instance object.")


def down():
  cloud.instance.down()


def delete(confirm=True):
  cloud.instance.delete(confirm)
