# from flask_jsonrpc.exceptions import Error


# class ApplicationError(Error):
class ApplicationError(Exception):
    """Базовый класс ошибки приложения"""

    def __init__(
            self,
            code: int = None,
            message: str = None,
            data: object = None,
            status: int = None,
            inner_exception: Exception = None):

        if code:
            self.code = code
        if message:
            self.message = message
        if data:
            self.data = data
        if status:
            self.status = status
        if inner_exception:
            self.inner_exception = inner_exception

    code = 1
    message = None
    data = None
    status = 500
    inner_exception = None
