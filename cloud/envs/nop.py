import logging
import random
import re
import socket
import string
import subprocess

import requests

from cloud.envs import env, registry, utils

logger = logging.getLogger(__name__)


@registry.register("nop")
class NOPInstance(env.Instance):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        return

    @property
    def driver(self):
        return NOPDriver()

    @property
    def name(self):
        return "nop"


class NOPDriver():
    def __init__(self):
        self.nodes = [NOPNode()]
        return

    def ex_stop_node(self, node):
        return

    def list_nodes(self):
        return self.nodes

    def destroy_node(self, node, **kwargs):
        return


class NOPNode():
    def __init__(self):
        return

    @property
    def name(self):
        if getattr(self, '_name', None) is None:
            self._name = "nop"
        return self._name
