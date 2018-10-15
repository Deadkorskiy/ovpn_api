from flask import Blueprint, request
import os
import logging
from src.settings import settings
from src.utils import json_custom_response, auth_required
from fabric.api import local
from fabric.api import settings as fabric_settings
import re


openvpn_client_bp = Blueprint('openvpn_client_bp', __name__, url_prefix='/api/openvpn/client')


@openvpn_client_bp.route("/build/<cluster_name>/<unique_client_name>", methods=['POST'])
@auth_required
def build_client(cluster_name, unique_client_name):
    """Создает ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)
    is_new = True

    cluster_dir = os.path.join(settings.CLUSTERS_ABS_DIR_PATH, str(cluster_name), settings.CLUSTER_POSTFIX_PATH)
    if not os.path.exists(cluster_dir) or not os.path.isdir(cluster_dir):
        return json_custom_response(errors_occured=[{'message': 'Invalid cluster'}], code=400)

    cluster_easy_rsa_path = os.path.join(cluster_dir, 'easy-rsa')
    server_ca_path = os.path.join(cluster_easy_rsa_path, 'pki/ca.crt')
    server_ta_key_path = os.path.join(cluster_dir, 'ta.key')
    client_common_path = os.path.join(cluster_dir, 'client-common.txt')

    # если клиент уже есть - отдадим то что есть, если нет - создадим
    client_crt_path = os.path.join(cluster_dir, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if os.path.exists(client_crt_path):
        is_new = False
    else:
        command = 'timeout 10 bash -c "cd {}; ./easyrsa build-client-full {} nopass"'.format(cluster_easy_rsa_path, unique_client_name)
        with fabric_settings(abort_exception=Exception):
            try:
                local(command)
            except Exception as e:
                logging.getLogger(__file__).error('Error during client {} building:{}'.format(unique_client_name, str(e)))
                return json_custom_response(errors_occured=[{'message': 'Building error'}], code=500)


    client_crt_path = os.path.join(cluster_easy_rsa_path, 'pki/issued/{}.crt'.format(unique_client_name))
    client_key_path = os.path.join(cluster_easy_rsa_path, 'pki/private/{}.key'.format(unique_client_name))
    client_req_path = os.path.join(cluster_easy_rsa_path, 'pki/reqs/{}.req'.format(unique_client_name))
    if not all([
        os.path.isfile(client_crt_path),
        os.path.isfile(client_key_path)
    ]):
        logging.getLogger(__file__).error('Client files was not created. cluster_name:{} unique_client_name:{}'. format(
            str(cluster_name),
            str(unique_client_name))
        )
        return json_custom_response(errors_occured=[{'message': 'An error occured during client creating'}], code=500)

    return json_custom_response(
        data={
            'client_key': open(client_key_path, 'r').read(),
            'client_crt': open(client_crt_path, 'r').read(),
            'client_req': open(client_req_path, 'r').read(),
            'server_ca': open(server_ca_path, 'r').read(),
            'server_ta_key': open(server_ta_key_path, 'r').read(),
            'client_common': open(client_common_path, 'r').read(),
            'client_name': unique_client_name,
            'is_new': is_new
        },
        code=200
    )


@openvpn_client_bp.route("/revoke/<cluster_name>/<unique_client_name>", methods=['POST'])
@auth_required
def revoke_client(cluster_name, unique_client_name):
    """Отзывает ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_dir = os.path.join(settings.CLUSTERS_ABS_DIR_PATH, str(cluster_name), settings.CLUSTER_POSTFIX_PATH)
    if not os.path.exists(cluster_dir) or not os.path.isdir(cluster_dir):
        return json_custom_response(errors_occured=[{'message': 'Invalid cluster'}], code=400)

    client_crt_path = os.path.join(cluster_dir, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if not os.path.exists(client_crt_path):
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_easy_rsa_path = os.path.join(cluster_dir, 'easy-rsa')

    with fabric_settings(abort_exception=Exception):
        try:
            local('timeout 5 bash -c "cd {} && echo yes | ./easyrsa revoke {}"'.format(cluster_easy_rsa_path, unique_client_name))
            local('timeout 5 bash -c "cd {} && ./easyrsa gen-crl"'.format(cluster_easy_rsa_path))
            local('cd {} && chmod 775 crl.pem'.format(os.path.join(cluster_easy_rsa_path, 'pki')))
        except Exception as e:
            logging.getLogger(__file__).error('Error during client {} revoke:{}'.format(unique_client_name, str(e)))
            return json_custom_response(errors_occured=[{'message': 'Revoke error'}], code=500)

    return json_custom_response(
        data={
            'message': 'Revoked',
            'client_name': unique_client_name,
        },
        code=200
    )


@openvpn_client_bp.route("/remove/<cluster_name>/<unique_client_name>", methods=['POST'])
@auth_required
def remove_client(cluster_name, unique_client_name):
    """Удаляет ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_dir = os.path.join(settings.CLUSTERS_ABS_DIR_PATH, str(cluster_name), settings.CLUSTER_POSTFIX_PATH)
    if not os.path.exists(cluster_dir) or not os.path.isdir(cluster_dir):
        return json_custom_response(errors_occured=[{'message': 'Invalid cluster'}], code=400)

    client_crt_path = os.path.join(cluster_dir, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if not os.path.exists(client_crt_path):
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_easy_rsa_path = os.path.join(cluster_dir, 'easy-rsa')

    with fabric_settings(abort_exception=Exception):
        try:
            local('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'private', unique_client_name + '.key')))
            local('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'issued', unique_client_name + '.crt')))
            local('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'reqs', unique_client_name + '.req')))
        except Exception as e:
            logging.getLogger(__file__).error('Error during client {} remove:{}'.format(unique_client_name, str(e)))
            return json_custom_response(errors_occured=[{'message': 'Remove error'}], code=500)

    return json_custom_response(
        data={
            'message': 'Revoked',
            'client_name': unique_client_name,
        },
        code=200
    )


@openvpn_client_bp.route("/load/<cluster_name>/<unique_client_name>", methods=['POST'])
@auth_required
def load_client(cluster_name, unique_client_name):
    """Загружает ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_dir = os.path.join(settings.CLUSTERS_ABS_DIR_PATH, str(cluster_name), settings.CLUSTER_POSTFIX_PATH)
    if not os.path.exists(cluster_dir) or not os.path.isdir(cluster_dir):
        return json_custom_response(errors_occured=[{'message': 'Invalid cluster'}], code=400)

    cluster_easy_rsa_path = os.path.join(cluster_dir, 'easy-rsa')

    body = request.get_json()
    key = body.get('data', {}).get('client_key', '')
    crt = body.get('data', {}).get('client_crt', '')
    req = body.get('data', {}).get('client_req', '')

    with fabric_settings(abort_exception=Exception):
        try:
            local('echo "{}" > {}'.format(key, os.path.join(cluster_easy_rsa_path, 'pki', 'private', unique_client_name + '.key')))
            local('echo "{}" > {}'.format(crt, os.path.join(cluster_easy_rsa_path, 'pki', 'issued', unique_client_name + '.crt')))
            local('echo "{}" > {}'.format(req, os.path.join(cluster_easy_rsa_path, 'pki', 'reqs', unique_client_name + '.req')))
        except Exception as e:
            logging.getLogger(__file__).error('Error during client {} load:{}'.format(unique_client_name, str(e)))
            return json_custom_response(errors_occured=[{'message': 'Load error'}], code=500)

    return json_custom_response(
        data={
            'message': 'Loaded',
            'client_name': unique_client_name,
        },
        code=200
    )


@openvpn_client_bp.route("/restore/<cluster_name>/<unique_client_name>", methods=['POST'])
@auth_required
def restore_client(cluster_name, unique_client_name):
    """Восстанавливает доступ ovpn клиенту"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_dir = os.path.join(settings.CLUSTERS_ABS_DIR_PATH, str(cluster_name), settings.CLUSTER_POSTFIX_PATH)
    if not os.path.exists(cluster_dir) or not os.path.isdir(cluster_dir):
        return json_custom_response(errors_occured=[{'message': 'Invalid cluster'}], code=400)

    client_crt_path = os.path.join(cluster_dir, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if not os.path.exists(client_crt_path):
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_easy_rsa_path = os.path.join(cluster_dir, 'easy-rsa')
    index_txt_path = os.path.join(cluster_easy_rsa_path, 'pki', 'index.txt')

    with fabric_settings(abort_exception=Exception):
        try:
            index_txt_content = ''
            with open(index_txt_path, 'r+') as f:
                index_txt_content = f.read()
                f.truncate()

            revoked_client_string = re.findall('R.{1,10}\d{1,12}.{1,700}CN=' + str(unique_client_name), index_txt_content)
            if len(revoked_client_string) != 1:
                return json_custom_response(errors_occured=[{'message': 'Client for restore not found'}], code=400)
            revoked_client_string = str(revoked_client_string[0])
            restored_client_string = \
                'V	{}		{}	{}	{}'.format(
                    revoked_client_string.split()[1],  # 280522060444Z
                    revoked_client_string.split()[3],  # 2A6DA37E9D7AFE75BC8E5DA18C0CDC62
                    revoked_client_string.split()[4],  # unknown
                    revoked_client_string.split()[5],  # /CN=1e3d210b-2862-4b68-a10a-43aff837ddfd
                )
            index_txt_content = index_txt_content.replace(revoked_client_string, restored_client_string)

            with open(index_txt_path, 'r+') as f:
                f.seek(0)
                f.write(index_txt_content)
                f.truncate()

            local('chmod 775 {}'.format(index_txt_path))
            local('timeout 5 bash -c "cd {} && ./easyrsa gen-crl"'.format(cluster_easy_rsa_path))
            local('cd {} && chmod 775 crl.pem'.format(os.path.join(cluster_easy_rsa_path, 'pki')))
        except Exception as e:
            logging.getLogger(__file__).error('Error during client {} restore:{}'.format(unique_client_name, str(e)))
            return json_custom_response(errors_occured=[{'message': 'Restore error'}], code=500)

    return json_custom_response(
        data={
            'message': 'Restored',
            'client_name': unique_client_name,
        },
        code=200
    )



#
# # restart
# # kick