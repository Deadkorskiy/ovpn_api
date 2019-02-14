from redis import StrictRedis
from src.settings import settings
from typing import Union
from .connection_string import BaseConnectionString, RedisConnectionString, MongoConnectionString


def get_db_gateway(label: str = 'default', connection_string: BaseConnectionString = None) -> Union[StrictRedis]:
    connection_string = connection_string if connection_string else settings.DATABASE[label]
    if connection_string['dbms'].lower() == 'redis':
        connection_string = RedisConnectionString(**connection_string)
        return StrictRedis(
            host=connection_string.host,
            port=connection_string.port,
            password=connection_string.password,
            db=connection_string.db
        )
    else:
        raise ValueError('Unknown db gateway')
