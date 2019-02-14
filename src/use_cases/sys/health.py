from src.base.use_case import BaseUseCaseRequest, BaseUseCase, BaseUseCaseResponse, ApplicationError
from src.utils import timeout
from src.utils import shell_cmd
from src.settings import settings
import os
import uuid
import re
import socket


class HealthUseCaseRequest(BaseUseCaseRequest):

    def is_valid(self, *args, **kwargs):
        return self


class HealthUseCaseResponse(BaseUseCaseResponse):
    pass


class HealthUseCase(BaseUseCase):

    class HealthCheckResponse(object):

        def __init__(self, service_name: str, is_up: bool, error: str = None, details: dict = None):
            self.is_up = is_up if error is None else False
            self.service_name = service_name
            self.error = error
            self.details = details if details else {}

        def serialize(self) -> dict:
            return {
                'service_name': str(self.service_name),
                'is_up': bool(self.is_up),
                'error': str(self.error),
                'details': self.details,
            }

    def __execute__(self, request:BaseUseCaseRequest, *args, **kwargs):
        main_service_result = self.HealthCheckResponse('main', False, details={'dependencies': []})
        try:

            checks = [
                (self.check_telnet, self.HealthCheckResponse('telnet', False)),
                (self.check_openvpn, self.HealthCheckResponse('openvpn', False)),
            ]

            check_results = []
            for row in checks:
                result = timeout(row[0], kwargs={'result': row[1]}, timeout=5, default=row[1])
                if result:
                    check_results.append(result)

            if all(map(lambda x: x.is_up, check_results)) and len(checks) == len(check_results):
                main_service_result.is_up = True

            for row in check_results:
                main_service_result.details['dependencies'].append(row.serialize())

            main_service_result.details['deploy'] = settings.BUILD_INFO

        except Exception as e:
            main_service_result.error = str(e)
        return HealthUseCaseResponse(value=main_service_result.serialize())

    def check_openvpn(self, result: HealthCheckResponse) -> HealthCheckResponse:
        try:
            output = ''
            output_tmp_file_name = os.path.join(
                settings.TMP_OUTPUT_DIR,
                'tmp_health_output_{}.txt'.format(str(uuid.uuid4()))

            )
            cmd = """timeout 7 bash -c 'HOST="{0}" && CMD="pid" && (echo open "$HOST" && sleep 2 && echo "$CMD" && sleep 2 && echo "exit") | telnet' > {1}""".format(
                settings.OPENVPN_TELNET_MANAGEMENT,
                output_tmp_file_name
            )
            try:
                shell_cmd(cmd)
            except Exception as e:
                with open(output_tmp_file_name, 'r') as f:
                    output = f.read()
                os.remove(output_tmp_file_name)

            pid = int(str(re.findall('SUCCESS: pid=\d{1,6}', output)[0]).replace('SUCCESS: pid=', ''))
            result.is_up = True
            result.details.update({'pid': pid})
        except Exception as e:
            result.error = str(e)
        return result

    def check_telnet(self, result: HealthCheckResponse) -> HealthCheckResponse:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            response = sock.connect_ex((settings.OPENVPN_TELNET_MANAGEMENT_HOST, settings.OPENVPN_TELNET_MANAGEMENT_PORT))
            if response == 0:
                result.is_up = True
            else:
                raise ApplicationError(message=str(response))
        except Exception as e:
            result.error = str(e)
        return result
