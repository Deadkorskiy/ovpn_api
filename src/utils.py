from typing import List
from flask import jsonify
from flask import make_response
from flask import Response
from flask import request
from .settings.settings import ACCESS_HEADERS, ACCESS_HEADER_NAME
from fabric.api import settings as fabric_settings
from fabric.api import local
import logging
import threading


def json_custom_response(
        data: dict = None,
        errors_occured: List[dict] = None,
        meta: dict = None,
        code: int = 200
) -> Response:

    api_response = {
        'meta': None,
        'data': None,
        'errors_occured': []
    }
    if data:
        api_response.update({ 'data': data})
    if meta:
        api_response.update({'meta': meta})
    if errors_occured:
        api_response.update({'errors_occured': errors_occured})
    return make_response(jsonify(api_response), code)


def auth_required(f):
    def wrapper(*args, **kwargs):
        if request.headers.get(ACCESS_HEADER_NAME) not in ACCESS_HEADERS:
            return json_custom_response(errors_occured=[{'message': 'Access denied'}], code=403)
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def shell_cmd(command: str, capture=True, shell=None, no_logs: bool = False) -> str:
    result = error = None
    with fabric_settings(abort_exception=Exception):
        try:
            result = str(local(command, capture=capture, shell=shell))
        except Exception as e:
            if not no_logs:
                logging.getLogger(__file__).error('Error during shell command execution. Command:"{}". Error:{}'.format(command, str(e)))
            error = e
        finally:
            logging.getLogger(__file__).debug(
                'CMD:"{}". RESULT:{}'.format(command, result))
            if error:
                raise error
            else:
                return result


def timeout(func, args: tuple=(), kwargs: dict = {}, timeout: int = 3, default=None):
    """Вызывает функцию с timeout-ом"""

    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout)
    result = getattr(it, 'result', default)
    return result if result is not None else default
