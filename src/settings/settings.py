import os


SRC_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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
    'server'
]

SECRET_KEY = 'aksjdfkj385602836547hajkdsfvn;skjdf;kjhIUGTUYOAD08544967597%(^%976fgawgef'

DEBUG = False

HOST = '127.0.0.1'

PORT = 5000



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
            "filename": os.path.abspath(os.path.join(SRC_ROOT, os.path.join(SRC_ROOT, 'var', 'log', 'api.log'))),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        # 'sentry': {
        #     'level': 'DEBUG',
        #     'class': 'raven.handlers.logging.SentryHandler',
        #     'dsn': SENTRY_DSN,
        # }
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
