from src.celery.application import celery_app
from .openvpn_events import ProcessOpenVPNEvents

# python -m celery -A src.rest.services.lazy_evaluation.celery_application worker -l info


@celery_app.task
def send_openvpn_events():
    job = ProcessOpenVPNEvents()
    job.do_work()