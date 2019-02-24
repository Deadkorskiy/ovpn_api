import os


SRC_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

BUILD_INFO_JSON_PATH = '{}/etc/build_info.json'.format(SRC_ROOT)

LOG_DIR_PATH = os.path.abspath(os.path.join(SRC_ROOT, 'var', 'log'))

TMP_OUTPUT_DIR = os.path.join(SRC_ROOT, 'var', 'tmp_output')

OPENVPN_PATH = '/etc/openvpn'

OPENVPN_TELNET_MANAGEMENT_HOST = '127.0.0.1'
OPENVPN_TELNET_MANAGEMENT_PORT = 7505
OPENVPN_TELNET_MANAGEMENT = '{} {}'.format(OPENVPN_TELNET_MANAGEMENT_HOST, str(OPENVPN_TELNET_MANAGEMENT_PORT))

ACCESS_HEADER_NAME = "api-key"

ACCESS_HEADERS = [
    "c18d6f66-d3bc-4ca3-8f1c-ea7235f04681"
]

IGNORED_CLIENT_NAMES = [    # low case only
    'server',
    'sys_health'
]

SECRET_KEY = 'aksjdfkj385602836547hajkdsfvn;skjdf;kjhIUGTUYOAD08544967597%(^%976fgawgef'

DEBUG = False

HOST = '127.0.0.1'

PORT = 5000

DATABASE = {
    'redis': {
        'dbms': 'redis',
        'host': '127.0.0.1',
        'port': 6379,
        'db': 1,
        'password': 'c1_redis_master_password'
    }
}

BUILD_INFO = {
    'commit': None,
    'datetime': None,
    'branch': None
}
try:
    import json
    __build_info__ = {}
    with open(BUILD_INFO_JSON_PATH, 'r') as f:
        __build_info__ = json.loads(f.read())
    BUILD_INFO['commit'] = __build_info__.get('commit')
    BUILD_INFO['branch'] = __build_info__.get('branch')
    BUILD_INFO['datetime'] = __build_info__.get('datetime')
except Exception as e:
    print('Deploy info load failure:{}'.format(str(e)))

SENTRY_DSN = ''

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
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "advanced",
            "filename": os.path.abspath(os.path.join(LOG_DIR_PATH, 'api.log')),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
    },
    "loggers": {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    }
}

TESTS_API_ADDRESS = 'http://{}:{}'.format(HOST, PORT)

TESTS_API_TOKEN = ACCESS_HEADERS[0]



try:
    from .local_settings import *
except ImportError:
    pass
