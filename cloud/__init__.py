import sys

import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
        'stdout': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
        'stderr': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'formatter': 'verbose',
        },
        'stderr': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'cloud': {
            'handlers': ['stderr', 'stdout'],
            'level': 'INFO',
            'propagate': False,
        },
    },
})

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

from cloud.cloud import connect
from cloud.cloud import down
from cloud.cloud import delete
