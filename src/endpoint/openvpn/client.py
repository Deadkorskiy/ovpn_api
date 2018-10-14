from flask import Blueprint
import os
import logging
from settings import settings
from utils import json_custom_response, auth_required
from fabric.api import local


client_bp = Blueprint('client_bp', __name__, url_prefix='/api/client/')


client_bp.route("/api/openvpn/client/build/<cluster_name>/<unique_client_name>")
# @auth_required
def build_client(cluster_name, unique_client_name):
    """Создает ovpn клиента"""

    unique_client_name = str(unique_client_name)
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
        command = 'cd {}; ./easyrsa build-client-full {} nopass'.format(cluster_easy_rsa_path, unique_client_name)
        local(command)

    client_crt_path = os.path.join(cluster_easy_rsa_path, 'pki/issued/{}.crt'.format(unique_client_name))
    client_key_path = os.path.join(cluster_easy_rsa_path, 'pki/private/{}.key'.format(unique_client_name))
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
            'server_ca': open(server_ca_path, 'r').read(),
            'server_ta_key': open(server_ta_key_path, 'r').read(),
            'client_common': open(client_common_path, 'r').read(),
            'client_name': unique_client_name,
            'is_new': is_new
        },
        code=200
    )


client_bp.route("/api/openvpn/client/revoke/<cluster_name>/<unique_client_name>")
# @auth_required
def revoke_client(cluster_name, unique_client_name):
    """Отзывает и удаляет ovpn клиента"""

    unique_client_name = str(unique_client_name)

    cluster_dir = os.path.join(settings.CLUSTERS_ABS_DIR_PATH, str(cluster_name), settings.CLUSTER_POSTFIX_PATH)
    if not os.path.exists(cluster_dir) or not os.path.isdir(cluster_dir):
        return json_custom_response(errors_occured=[{'message': 'Invalid cluster'}], code=400)

    client_crt_path = os.path.join(cluster_dir, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if not os.path.exists(client_crt_path):
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_easy_rsa_path = os.path.join(cluster_dir, 'easy-rsa')

    # revoke
    local('cd {} && ./easyrsa revoke {}'.format(cluster_easy_rsa_path, unique_client_name))
    local('cd {} && ./easyrsa gen-crl'.format(cluster_easy_rsa_path))
    local('cd {} && chmod 775 crl.pem'.format(os.path.join(cluster_easy_rsa_path, 'pki')))

    # remove
    local('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'private', unique_client_name + '.key')))
    local('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'issued', unique_client_name + '.crt')))
    local('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'reqs', unique_client_name + '.req')))

    return json_custom_response(
        data={
            'message': 'Ok',
            'client_name': unique_client_name,
        },
        code=200
    )
