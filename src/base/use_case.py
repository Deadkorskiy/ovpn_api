from .exception import ApplicationError
import logging


class BaseUseCaseRequest(object):

    def __init__(self, *args, **kwargs):
        self.errors = []

    def add_error(self, error: Exception)->None:
        self.errors.append(error)

    def has_errors(self)->bool:
        return len(self.errors) > 0

    @classmethod
    def deserialize(cls, data: dict) ->'BaseUseCaseRequest':
        raise NotImplementedError()

    def is_valid(self, *args, **kwargs)-> 'BaseUseCaseRequest':
        raise NotImplementedError()

    def __nonzero__(self)->bool:
        return not self.has_errors()

    __bool__ = __nonzero__


class BaseUseCaseResponse(object):

    def __init__(self, value=None, *args, **kwargs):
        self.errors = []
        self.value = value

    def add_error(self, error: Exception)->None:
        self.errors.append(error)

    def has_errors(self)->bool:
        return len(self.errors) > 0

    def __nonzero__(self)->bool:
        return not self.has_errors()

    __bool__ = __nonzero__

    @classmethod
    def build_from_exception(cls, exception: Exception):
        if not issubclass(type(exception), ApplicationError):
            exception = ApplicationError(inner_exception=exception)
        instance = cls()
        instance.errors.extend([exception])
        return instance

    @classmethod
    def build_from_invalid_request(cls, invalid_request: 'BaseUseCaseRequest') -> 'BaseUseCaseResponse':
        instance = cls()
        instance.errors.extend(invalid_request.errors)
        return instance


class BaseUseCase(object):

    def execute(self, request:BaseUseCaseRequest, *args, **kwargs) -> BaseUseCaseResponse:
        request = request.is_valid()
        if bool(request):
            try:
                return self.__execute__(request)
            except Exception as e:
                logging.getLogger(__file__).critical('Unhandled use_case error:{}'.format(str(e)))
                return BaseUseCaseResponse.build_from_exception(ApplicationError(inner_exception=e))
        else:
            return BaseUseCaseResponse.build_from_invalid_request(request)

    def __execute__(self, request:BaseUseCaseRequest, *args, **kwargs) -> BaseUseCaseResponse:
        raise NotImplementedError()
