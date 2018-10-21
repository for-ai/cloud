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

    raise Exception(
        f"Call to `{c}` failed {retry_count} times. Aborting. {out}")
