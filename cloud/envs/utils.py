import logging
import multiprocessing
import os
import subprocess
import time

from errand_boy.run import main as eb_main
from errand_boy.transports.unixsocket import UNIXSocketTransport

import cloud

logger = logging.getLogger(__name__)

EB_TRANSPORT = None
EB_SERVER = None


def get_transport():
    global EB_TRANSPORT
    if EB_TRANSPORT is None:
        EB_TRANSPORT = UNIXSocketTransport(socket_path=cloud.socket_path)
    return EB_TRANSPORT


def kill_transport():
    global EB_TRANSPORT
    if EB_TRANSPORT is None:
        return

    logger.warn("Killing transport")
    del EB_TRANSPORT
    EB_TRANSPORT = None


def _server_fn(socket_path):
    server = UNIXSocketTransport(socket_path=socket_path)
    server.run_server()


def get_server():
    global EB_SERVER
    if EB_SERVER is None:
        EB_SERVER = multiprocessing.Process(target=_server_fn, args=(cloud.socket_path,))
        EB_SERVER.start()
        time.sleep(3)
        logging.getLogger("errand_boy").setLevel(logging.ERROR)
    return EB_SERVER


def kill_server():
    global EB_SERVER
    if EB_SERVER is None:
        return

    logger.warn("Killing server")
    if EB_SERVER.is_alive():
        EB_SERVER.terminate()
        time.sleep(0.5)
    EB_SERVER.join(timeout=1)
    del EB_SERVER
    EB_SERVER = None


def call(cmd):
    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    stdout, stderr, returncode = get_transport().run_cmd(cmd)
    return returncode, stdout.decode("utf-8"), stderr.decode("utf-8")


def try_call(cmd, retry_count=5):
    c = cmd
    status = -1
    for _ in range(retry_count):
        if callable(cmd):
            c = cmd()
        status, stdout, stderr = call(c)
        if status == 0:
            logger.debug("Call to `{}` successful".format(c))
            return c
        else:
            logger.debug("Call to `{}` failed with status: {}. Retrying...".format(c, status))

    raise Exception("Call to `{}` failed {} times."
                    "Aborting.\n STDOUT: {}\n STDERR: {}".format(c, retry_count, stdout, stderr))


def config_path():
    path = os.environ.get("CLOUD_CFG")
    if path is not None and os.path.isfile(path):
        return path
    logger.debug("Unable to find config file at path: {}".format(path))

    path = os.path.join(os.environ["HOME"], "cloud.toml")
    if os.path.isfile(path):
        return path
    logger.debug("Unable to find config file at path: {}".format(path))

    path = "/cloud.toml"
    if os.path.isfile(path):
        return path
    logger.debug("Unable to find config file at path: {}".format(path))

    return None
