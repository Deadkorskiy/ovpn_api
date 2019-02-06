from flask import Blueprint
import logging
import os
from src.settings import settings
from src.utils import json_custom_response, auth_required
from fabric.api import settings as fabric_settings
import uuid
from ...utils import shell_cmd


openvpn_management_bp = Blueprint('openvpn_management_bp', __name__, url_prefix='/api/openvpn/management')


@openvpn_management_bp.route("/load-stats/", methods=['POST'])
@auth_required
def load_stats():
    """Кол-во подклченных пользователей"""
    output = ''
    output_tmp_file_name = os.path.join(
        settings.TMP_OUTPUT_DIR,
        'tmp_load-stats_output_{}.txt'.format(str(uuid.uuid4()))

    )
    cmd = """timeout 7 bash -c 'HOST="{0}" && CMD="load-stats" && (echo open "$HOST" && sleep 2 && echo "$CMD" && sleep 2 && echo "exit") | telnet' > {1}""".format(
        settings.OPENVPN_TELNET_MANAGEMENT,
        output_tmp_file_name
    )
    try:
        with fabric_settings(abort_exception=Exception):
            try:
                # Эта штука работает, но всегда падает из-за exit и timeout по этому выхлоп вытягивается через файл
                shell_cmd(cmd)
            except Exception:
                with open(output_tmp_file_name, 'r') as f:
                    output = f.read()

        return json_custom_response(
            data={
                'raw': str(output)
            },
            code=200
        )
    except Exception as e1:
        logging.getLogger(__file__).error('Error during load stats {}:{}'.format(output_tmp_file_name, str(e1)))
        return json_custom_response(
            errors_occured=[{'message': 'Load stats error', 'Internal error': str(e1)}],
            code=500
        )
    finally:
        try:
            os.remove(output_tmp_file_name)
        except Exception as e2:
            logging.getLogger(__file__).error('Error during remove {}:{}'.format(output_tmp_file_name, str(e2)))


@openvpn_management_bp.route("/restart/", methods=['POST'])
@auth_required
def restart():
    """Кол-во подклченных пользователей"""
    output = ''
    output_tmp_file_name = os.path.join(
        settings.TMP_OUTPUT_DIR,
        'tmp_restart_output_{}.txt'.format(str(uuid.uuid4()))

    )
    cmd = """timeout 120 bash -c 'supervisorctl restart openvpn > {}'""".format(
        output_tmp_file_name
    )
    try:
        with fabric_settings(abort_exception=Exception):
            try:
                # Эта штука работает, но всегда падает из-за exit и timeout по этому выхлоп вытягивается через файл
                shell_cmd(cmd)
            finally:
                with open(output_tmp_file_name, 'r') as f:
                    output = f.read()

        return json_custom_response(
            data={
                'raw': str(output)
            },
            code=200
        )
    except Exception as e1:
        logging.getLogger(__file__).error('Error during restart {}:{}'.format(output_tmp_file_name, str(e1)))
        return json_custom_response(
            errors_occured=[{'message': 'Restart error', 'Internal error': str(e1)}],
            code=500
        )
    finally:
        try:
            os.remove(output_tmp_file_name)
        except Exception as e2:
            logging.getLogger(__file__).error('Error during remove {}:{}'.format(output_tmp_file_name, str(e2)))
