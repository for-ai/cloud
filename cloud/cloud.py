import atexit
import logging
import os

import libcloud
import toml

import cloud
from cloud import Instance
from cloud import registry as reg
from cloud.envs import utils

logger = logging.getLogger(__name__)


def connect(socket_path="/tmp/cloud_socket"):
    config_filepath = utils.config_path()
    if config_filepath is None:
        logger.error("ASSUMING LOCAL: Configuration file not found in any of the locations"
                     " below.\n See github.com/for-ai/cloud/tree/master/configs for "
                     "example configurations to fill in and use; copy and place in a file "
                     "named `cloud.toml` at `/cloud.toml` or `$HOME/cloud.toml`.")
        return

    with open(config_filepath, "r") as cf:
        config = toml.load(cf)
        provider = config.pop("provider").lower()
        if socket_path:
            _set_socket_path(socket_path)
        cloud.instance = reg.retrieve(provider, config=config)


def _set_socket_path(local_socket_path):
    os.makedirs(os.path.dirname(local_socket_path), exist_ok=True)
    cloud.socket_path = local_socket_path


def close():
    utils.kill_transport()
    utils.kill_server()


def down():
    cloud.instance.down()


def delete(confirm=True):
    cloud.instance.delete(confirm)


atexit.register(close)
