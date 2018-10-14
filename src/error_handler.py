from .utils import json_custom_response
from flask import Response
from flask import request as flask_request
import typing
from werkzeug.exceptions import HTTPException
import logging


def __exception_to_response__(error: 'typing.Union[Exception, HTTPException]') -> Response:

    request_info = "Client:{}, URL:{} Method:{}, BaseURL:{} RootURL:{} FullPath:{} \
    Path:{} QueryString:{} Host:{} HostURL:{}".format(
        str(getattr(flask_request, 'remote_addr', '')),
        str(getattr(flask_request, 'url', '')),
        str(getattr(flask_request, 'method', '')),
        str(getattr(flask_request, 'base_url', '')),
        str(getattr(flask_request, 'url_root', '')),
        str(getattr(flask_request, 'full_path', '')),
        str(getattr(flask_request, 'path', '')),
        str(getattr(flask_request, 'query_string', '')),
        str(getattr(flask_request, 'host', '')),
        str(getattr(flask_request, 'host_url', ''))
    )
    logging.getLogger(__file__).error("API error: {} Additional info:[{}]".format(str(error), request_info))

    if isinstance(error, HTTPException):
        errors_occured = [{
            'message': getattr(error, 'name', 'Unknown error')
        }]
        return json_custom_response(errors_occured=errors_occured, code=getattr(error, 'code', 500))
    errors_occured = [{
        'message': 'Unknown error',
    }]
    return json_custom_response(errors_occured=errors_occured, code=500)


def error_handler(error: 'typing.Union[Exception, HTTPException]') -> Response:
    return __exception_to_response__(error)
