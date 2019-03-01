import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '../../../../')))
from src.settings import settings
sys.path.append(settings.SRC_ROOT)


from src.settings import settings
from celery import Celery

__CELERY__APPLICATION__ = None


def __get_celery_application__() -> Celery:
    global __CELERY__APPLICATION__

    if __CELERY__APPLICATION__:
        return __CELERY__APPLICATION__

    __CELERY__APPLICATION__ = Celery(
        'celery',
        broker=settings.CELERY_BROKER,
        include=settings.CELERY_INCLUDE
    )
    __CELERY__APPLICATION__.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE
    __CELERY__APPLICATION__.conf.timezone = 'UTC'

    return __get_celery_application__()


celery_app = __get_celery_application__()


@celery_app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

