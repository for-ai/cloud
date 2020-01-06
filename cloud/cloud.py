import atexit
import logging

import cloud
import libcloud
import toml
from cloud import Instance
from cloud import registry as reg
from cloud.envs import utils

logger = logging.getLogger(__name__)


def connect():
  config_filepath = utils.config_path()
  if config_filepath is None:
    logger.error(
        "ASSUMING LOCAL: Configuration file not found in any of the locations"
        " below.\n See github.com/for-ai/cloud/tree/master/configs for "
        "example configurations to fill in and use; copy and place in a file "
        "named `cloud.toml` at `/cloud.toml` or `$HOME/cloud.toml`.")
    return

  with open(config_filepath, "r") as cf:
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
