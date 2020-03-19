import sys
import logging

global logger
logger = logging.getLogger("cloud")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT, None))
logger.addHandler(handler)

logging.getLogger("errand_boy").setLevel(logging.WARNING)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)

socket_path = None

from cloud.envs import registry

from cloud.envs import env
from cloud.envs.env import Instance
from cloud.envs.env import Resource
from cloud.envs.env import ResourceManager

from cloud.envs import aws
from cloud.envs.aws import AWSInstance

from cloud.envs import azure
from cloud.envs.azure import AzureInstance

from cloud.envs import gcp
from cloud.envs.gcp import GCPInstance
from cloud.envs.gcp import TPU
from cloud.envs.gcp import TPUManager

from cloud.cloud import close
from cloud.cloud import connect
from cloud.cloud import down
from cloud.cloud import delete
