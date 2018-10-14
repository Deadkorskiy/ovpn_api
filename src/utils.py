from typing import List
from flask import jsonify
from flask import make_response
from flask import Response
from flask import request
from .settings.settings import ACCESS_HEADERS, ACCESS_HEADER_NAME


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
