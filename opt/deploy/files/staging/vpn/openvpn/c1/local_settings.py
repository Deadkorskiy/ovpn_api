import os


SRC_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

TMP_OUTPUT_DIR = os.path.join(SRC_ROOT, 'var', 'tmp_output')

OPENVPN_PATH = '/etc/openvpn'

ACCESS_HEADERS = [
    "c18d6f66-d3bc-4ca3-8f1c-ea7235f04681"
]

SECRET_KEY = 'sdjfkgb;ds98327498236hfkhKSJHDF:KSUDHf9w83423'

SENTRY_DSN = 'https://d0622ca859e646d48ccc190d6eba1d37:25f5d3ae5e444ba5b3131c7d04687e38@sentry.onetimevpn.com/5?verify_ssl=0'

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
            "level": "INFO",
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
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
        }
    },
    "loggers": {
        '': {
            'handlers': ['console', 'file', 'sentry'],
            'level': 'ERROR',
        },
    }
}