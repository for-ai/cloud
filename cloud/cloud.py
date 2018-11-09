import atexit
import libcloud
import logging
import toml

import cloud
from cloud import registry as reg
from cloud import Instance
from cloud.envs import utils

logger = logging.getLogger(__name__)


def connect():
  with open(utils.config_path(), "r") as cf:
    config = toml.load(cf)
    provider = config.pop("provider").lower()
    cloud.instance = reg.retrieve(provider, config=config)


def close():
  utils.kill_transport()
  utils.kill_server()


def down():
  cloud.instance.down()


def delete(confirm=True):
  cloud.instance.delete(confirm)


atexit.register(close)
