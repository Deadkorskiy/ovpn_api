import os


SRC_ROOT = os.path.abspath(os.path.join(__file__, '../../../'))
TEMPLATES_PATH = os.path.abspath(os.path.join(SRC_ROOT, 'rest/services/web_ui/templates/'))
STATIC_PATH = os.path.abspath(os.path.join(SRC_ROOT, 'rest/services/web_ui/static/'))

SENTRY_DSN = 'https://6e24b0a9d9a4402abb5284cac3efc596:a36a64070dfd42d29ccd23786a31676f@sentry.onetimevpn.com/3?verify_ssl=0'

STATIC_URL = '/static'

MEDIA_URL = '/media'

# куда класть клиентские ключи на впн сервере
REMOTE_CLIENT_DIR_PATH = '/home/deploy/onetimevpn/docker_persistent/openvpn/openvpn/easy-rsa/pki/'

SSH_ID_RSA_PATH = os.path.abspath(os.path.join(
    SRC_ROOT,
    '../etc/id_rsa')
)

SSH_USERNAME = 'deploy'

SSH_PASSWORD = 'aksdnv764VGGHS2636sFCrfcasasdfca'

CELERY_APP_NAME = 'celery_onetimevpn'

CELERY_INCLUDE = [
    'src.rest.services.lazy_evaluation.jobs.tasks',
    'src.rest.services.lazy_evaluation.tasks.tasks'
]

CELERY_BEAT_SCHEDULE = {
    'sustain_available_clients': {
        'task': 'src.rest.services.lazy_evaluation.jobs.tasks.sustain_crt_job',
        'schedule': float(60)
    },
    'revoke_expired_clients': {
        'task': 'src.rest.services.lazy_evaluation.jobs.tasks.revoke_expired_crt_job',
        'schedule': float(60)
    },
    'fake_user_count': {
        'task': 'src.rest.services.lazy_evaluation.jobs.tasks.fake_user_count_job',
        'schedule': float(60 * 5)  # every 5 minutes
    }
}

# за 5 минут
FREE_CRT_TIME_LIMIT_TIMESTAMP = float(60 * 5)
# можно скачать только 5 сертфиката
FREE_CRT_TIME_LIMIT_COUNT = 300


############################### OVERRIDE BELOW SETTINGS AT local_settings.py #########################################


SECRET_KEY = 'vnasdfasBOUK:L<097523ihbcsjbJGFCYIFSDV CWD647rdfw2BC'

DEBUG = False

HOST = '127.0.0.1'

PORT = 5000

SESSION_STORAGE = {
    'redis': {
        'host': '127.0.0.1',
        'port':6379,
        'db':1
    }
}

DATABASE = {
    'default':{
        'dbms':'mongodb',
        'host': '127.0.0.1',
        'port': 27017,
        'db': 'onetimevpn',
        'user': 'onetimevpn',
        'password': 'onetimevpn',
        'auth_source': 'onetimevpn'
    }
}

MAILING_CONFIGURATION = {
    "MAIL_SERVER": 'smtp.sendgrid.net',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'apikey',
    "MAIL_PASSWORD": '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'    # prod account
}

MAIL_STATIC_URL = 'https://staging.onetimevpn.com/static/assets/img/mail/'

URL = "https://staging.onetimevpn.com/"

CELERY_BROKER = 'amqp://guest:guest@127.0.0.1:5672'

TELEGRAM_FEEDBACK_BOT_TOKEN = "638273259:AAGdDppCyjbyKUFoT5j5NQFO90A--3NJpU8"
TELEGRAM_FEEDBACK_BOT_ADMIN_IDS = [
    38203606  # deadkorskiy
]
TELEGRAM_FEEDBACK_BOT_DESTINATION_CHANNEL_ID: int = -264650303


LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "advanced": {
            "format": "[%(asctime)s] [PID: %(process)6d] [%(filename)20s:%(lineno)4s] [%(levelname)8s] ---> %(message)s "
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "advanced",
            "filename": os.path.abspath(os.path.join(SRC_ROOT, '../var/log/http_api.log')),
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
            'handlers': ['sentry', 'file'],
            'level': 'ERROR',
        },
    }
}