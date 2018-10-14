import os

CLUSTERS_ABS_DIR_PATH = '/mnt/5FDF25D5580592D3/Lab/onetimevpn/opt/deploy/docker/files/staging/vpn/openvpn'

CLUSTER_POSTFIX_PATH = 'openvpn'

ACCESS_HEADER_NAME = "Api-Key"

ACCESS_HEADERS = [
    "c18d6f66-d3bc-4ca3-8f1c-ea7235f04681"
]

SECRET_KEY = 'aksjdfkj385602836547hajkdsfvn;skjdf;kjhIUGTUYOAD08544967597%(^%976fgawgef'

DEBUG = False

LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "advanced": {
            "format":
            "[%(asctime)s] [PID: %(process)6d] [%(filename)20s:%(lineno)4s] [%(levelname)8s] ---> %(message)s "
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "advanced",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

try:
    from .local_settings import *
except ImportError:
    pass
