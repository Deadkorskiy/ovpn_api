class BaseConnectionString(object):

    def __init__(
            self,
            dbms: str,
            host: str,
            port: int,
            db: str,
            user: str = None,
            password: str = None,
            *args, **kwargs
    ):
        self.dbms = dbms
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

    def __to_string__(self) -> str:
        if self.user:
            user_password = '{}:{}@'.format(self.user, self.password)
        else:
            user_password = ''
        return '{}://{}{}:{}'.format(
            self.dbms,
            user_password,
            self.host,
            self.port
        )

    __str__ = __to_string__


class MongoConnectionString(BaseConnectionString):

    def __init__(
            self,
            dbms: str,
            host: str,
            port: int,
            db: str,
            user: str = None,
            password: str = None,
            *args, **kwargs
    ):
        super().__init__(dbms, host, port, db, user, password)
        self.kwargs = kwargs

    def __to_string__(self) -> str:
        user_password = ''
        if self.user:
            user_password = '{}:{}@'.format(self.user, self.password)
        else:
            user_password = ''
        connection_string = '{}://{}{}'.format(
            self.dbms,
            user_password,
            self.host
        )
        options = '&'.join(["{}={}".format(key, value) for key, value in self.kwargs.items()])
        return '{}/?{}'.format(connection_string, options)

    __str__ = __to_string__


class RedisConnectionString(BaseConnectionString):
    pass
