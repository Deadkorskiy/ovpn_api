import os
import sys
SRC_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(SRC_ROOT)


from src.bootstrap import bootstrap, get_application
from src.settings import settings


bootstrap()
application = get_application()


if __name__ == '__main__':
        application.run(
            debug=settings.DEBUG,
            host=settings.HOST,
            port=settings.PORT
        )
