import logging
import os
import subprocess


def call(cmd):
  cp = subprocess.run(cmd, stdout=subprocess.PIPE)
  return cp.returncode, cp.stdout.decode("utf-8")


def try_call(cmd, retry_count=5):
  c = cmd
  status = -1
  for _ in range(retry_count):
    if callable(cmd):
      c = cmd()
    status, out = call(c)
    if status == 0:
      logging.debug(f"Call to `{c}` successful")
      return c
    else:
      logging.debug(f"Call to `{c}` failed with status: {status}. Retrying...")

  raise Exception(f"Call to `{c}` failed {retry_count} times. Aborting. {out}")


def config_path():
  path = os.environ.get("CLOUD_CFG")
  if path is not None and os.path.isfile(path):
    return path
  logging.warn(f"Unable to find config file at path: {path}")

  path = os.path.join(os.environ["HOME"], "cloud.toml")
  if os.path.isfile(path):
    return path
  logging.warn(f"Unable to find config file at path: {path}")

  path = "/cloud.toml"
  if os.path.isfile(path):
    return path
  logging.warn(f"Unable to find config file at path: {path}")

  raise Exception("Configuration file not found in any of the above locations."
                  "\n See cloud/configs for example configurations to fill in "
                  "and use; copy and place in a file named `cloud.toml` at "
                  "`/cloud.toml` or `$HOME/cloud.toml`.")
