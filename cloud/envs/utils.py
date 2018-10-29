import logging
import os
import subprocess

from errand_boy.transports.unixsocket import UNIXSocketTransport

EB_TRANSPORT = UNIXSocketTransport()

logger = logging.getLogger(__name__)


def call(cmd):
  if isinstance(cmd, list):
    cmd = " ".join(cmd)

  global EB_TRANSPORT
  stdout, stderr, returncode = EB_TRANSPORT.run_cmd(cmd)
  return returncode, stdout.decode("utf-8"), stderr.decode("utf-8")


def try_call(cmd, retry_count=5):
  c = cmd
  status = -1
  for _ in range(retry_count):
    if callable(cmd):
      c = cmd()
    status, stdout, stderr = call(c)
    if status == 0:
      logger.debug(f"Call to `{c}` successful")
      return c
    else:
      logger.debug(f"Call to `{c}` failed with status: {status}. Retrying...")

  raise Exception(f"Call to `{c}` failed {retry_count} times. Aborting. {out}")


def config_path():
  path = os.environ.get("CLOUD_CFG")
  if path is not None and os.path.isfile(path):
    return path
  logger.warn(f"Unable to find config file at path: {path}")

  path = os.path.join(os.environ["HOME"], "cloud.toml")
  if os.path.isfile(path):
    return path
  logger.warn(f"Unable to find config file at path: {path}")

  path = "/cloud.toml"
  if os.path.isfile(path):
    return path
  logger.warn(f"Unable to find config file at path: {path}")

  raise Exception("Configuration file not found in any of the above locations."
                  "\n See cloud/configs for example configurations to fill in "
                  "and use; copy and place in a file named `cloud.toml` at "
                  "`/cloud.toml` or `$HOME/cloud.toml`.")
