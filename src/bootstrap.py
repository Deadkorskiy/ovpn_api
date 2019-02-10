from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from .settings import settings
import logging.config


__APPLICATION__ = None


def get_application() -> Flask:
    global __APPLICATION__
    if __APPLICATION__:
        return __APPLICATION__

    __APPLICATION__ = Flask(__name__)
    __APPLICATION__.url_map.strict_slashes = False
    __APPLICATION__secret_key = settings.SECRET_KEY
    __APPLICATION__.wsgi_app = ProxyFix(__APPLICATION__.wsgi_app)
    return get_application()


def __register_blueprint__():
    from src.endpoint.openvpn.client import openvpn_client_bp
    get_application().register_blueprint(openvpn_client_bp)

    from src.endpoint.openvpn.management import openvpn_management_bp
    get_application().register_blueprint(openvpn_management_bp)

    from src.endpoint.sys import sys_bp
    get_application().register_blueprint(sys_bp)


def __register_error_handler__() -> None:
    from .error_handler import error_handler
    get_application().register_error_handler(Exception, error_handler)

    from werkzeug.exceptions import (
        BadRequest,
        Unauthorized,
        Forbidden,
        NotFound,
        MethodNotAllowed,
        NotAcceptable,
        RequestTimeout,
        Conflict,
        Gone,
        LengthRequired,
        PreconditionFailed,
        RequestEntityTooLarge,
        RequestURITooLarge,
        UnsupportedMediaType,
        RequestedRangeNotSatisfiable,
        ExpectationFailed,
        ImATeapot,
        UnprocessableEntity,
        Locked,
        PreconditionRequired,
        TooManyRequests,
        RequestHeaderFieldsTooLarge,
        UnavailableForLegalReasons,
        InternalServerError,
        NotImplemented,
        BadGateway,
        ServiceUnavailable,
        GatewayTimeout,
        HTTPVersionNotSupported
    )
    get_application().register_error_handler(NotFound, error_handler)
    get_application().register_error_handler(BadRequest, error_handler)
    get_application().register_error_handler(Unauthorized, error_handler)
    get_application().register_error_handler(Forbidden, error_handler)
    get_application().register_error_handler(MethodNotAllowed, error_handler)
    get_application().register_error_handler(NotAcceptable, error_handler)
    get_application().register_error_handler(RequestTimeout, error_handler)
    get_application().register_error_handler(Conflict, error_handler)
    get_application().register_error_handler(Gone, error_handler)
    get_application().register_error_handler(LengthRequired, error_handler)
    get_application().register_error_handler(PreconditionFailed, error_handler)
    get_application().register_error_handler(RequestEntityTooLarge, error_handler)
    get_application().register_error_handler(RequestURITooLarge, error_handler)
    get_application().register_error_handler(UnsupportedMediaType, error_handler)
    get_application().register_error_handler(RequestedRangeNotSatisfiable, error_handler)
    get_application().register_error_handler(ExpectationFailed, error_handler)
    get_application().register_error_handler(ImATeapot, error_handler)
    get_application().register_error_handler(UnprocessableEntity, error_handler)
    get_application().register_error_handler(Locked, error_handler)
    get_application().register_error_handler(PreconditionRequired, error_handler)
    get_application().register_error_handler(TooManyRequests, error_handler)
    get_application().register_error_handler(RequestHeaderFieldsTooLarge, error_handler)
    get_application().register_error_handler(UnavailableForLegalReasons, error_handler)
    get_application().register_error_handler(InternalServerError, error_handler)
    get_application().register_error_handler(NotImplemented, error_handler)
    get_application().register_error_handler(BadGateway, error_handler)
    get_application().register_error_handler(ServiceUnavailable, error_handler)
    get_application().register_error_handler(GatewayTimeout, error_handler)
    get_application().register_error_handler(HTTPVersionNotSupported, error_handler)


def bootstrap() -> None:
    logging.config.dictConfig(settings.LOGGING_CONFIGURATION)
    get_application()
    __register_blueprint__()
    __register_error_handler__()


