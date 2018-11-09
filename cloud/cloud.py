import libcloud
import toml

import cloud
from cloud import registry as reg
from cloud import Instance
from cloud.envs import utils


def connect():
  with open(utils.config_path(), "r") as cf:
    config = toml.load(cf)
    provider = config.pop("provider").lower()
    cloud.instance = reg.retrieve(provider, config=config)


def quit():
  logger.warn("Killing transport")
  utils.kill_transport()
  logger.warn("Killing server")
  utils.kill_server()


def down():
  cloud.instance.down()


def delete(confirm=True):
  cloud.instance.delete(confirm)
