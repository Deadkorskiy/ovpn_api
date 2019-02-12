from flask import Blueprint, request
import os
import logging
from src.settings import settings
from src.utils import json_custom_response, auth_required
from fabric.api import settings as fabric_settings
import re
import uuid
from datetime import datetime
from ...utils import shell_cmd


openvpn_client_bp = Blueprint('openvpn_client_bp', __name__, url_prefix='/api/openvpn/client')


@openvpn_client_bp.route("/build/<unique_client_name>", methods=['POST'])
@auth_required
def build_client(unique_client_name):
    """Создает ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)
    is_new = True

    client_common_path = os.path.join(settings.OPENVPN_PATH, 'client-common.txt')
    cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')
    server_ca_path = os.path.join(cluster_easy_rsa_path, 'pki/ca.crt')
    server_ta_key_path = os.path.join(cluster_easy_rsa_path, 'pki/ta.key')

    # если клиент уже есть - отдадим то что есть, если нет - создадим
    client_crt_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if os.path.exists(client_crt_path):
        is_new = False
    else:
        command = 'timeout 10 bash -c "cd {}; ./easyrsa build-client-full {} nopass"'.format(cluster_easy_rsa_path, unique_client_name)
        try:
            shell_cmd(command, capture=True)
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
        logging.getLogger(__file__).error('Client files was not created. unique_client_name:{}'. format(
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


@openvpn_client_bp.route("/revoke/<unique_client_name>", methods=['POST'])
@auth_required
def revoke_client(unique_client_name):
    """Отзывает ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    client_crt_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if not os.path.exists(client_crt_path):
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')

    try:
        shell_cmd('timeout 5 bash -c "cd {} && echo yes | ./easyrsa revoke {}"'.format(cluster_easy_rsa_path, unique_client_name))
        shell_cmd('timeout 5 bash -c "cd {} && ./easyrsa gen-crl"'.format(cluster_easy_rsa_path))
        shell_cmd('cd {} && chmod 775 crl.pem'.format(os.path.join(cluster_easy_rsa_path, 'pki')))
    except Exception as e:

        # Если сертификат уже отозван отдаем 200
        try:
            cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')
            index_txt_path = os.path.join(cluster_easy_rsa_path, 'pki', 'index.txt')
            index_txt_content = ''
            with open(index_txt_path, 'r+') as f:
                index_txt_content = f.read()
                f.truncate()
            revoked_client_string = re.findall(
                '[R].{1,10}\d{1,12}.{1,700}CN=' + str(unique_client_name) + '.{0,150}\n',
                index_txt_content
            )
            if len(revoked_client_string) > 0:
                return json_custom_response(
                    data={
                        'message': 'Already revoked',
                        'client_name': unique_client_name,
                    },
                    code=200
                )
        except Exception as e2:
            logging.getLogger(__file__).error('Revoke error, during ensure that crt already revoked. Error:{}'.format(str(e2)))


        logging.getLogger(__file__).error('Error during client {} revoke:{}'.format(unique_client_name, str(e)))
        return json_custom_response(errors_occured=[{'message': 'Revoke error'}], code=500)

    return json_custom_response(
        data={
            'message': 'Revoked',
            'client_name': unique_client_name,
        },
        code=200
    )


@openvpn_client_bp.route("/remove/<unique_client_name>", methods=['POST'])
@auth_required
def remove_client(unique_client_name):
    """Удаляет ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    client_crt_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if not os.path.exists(client_crt_path):
        return json_custom_response(
            data={
                'message': 'Already removed',
                'client_name': unique_client_name,
            },
            code=200
        )

    cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')

    # Если сертификат не отозван его нельзя удалять
    try:
        cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')
        index_txt_path = os.path.join(cluster_easy_rsa_path, 'pki', 'index.txt')
        index_txt_content = ''
        with open(index_txt_path, 'r+') as f:
            index_txt_content = f.read()
            f.truncate()
        revoked_client_string = re.findall(
            '[R].{1,10}\d{1,12}.{1,700}CN=' + str(unique_client_name) + '.{0,150}\n',
            index_txt_content
        )
        if len(revoked_client_string) < 1:
            return json_custom_response(errors_occured=[{'message': 'Client is not revoked'}], code=400)
    except Exception as e2:
        logging.getLogger(__file__).error(
            'Revoke error, during ensure that crt already revoked. Error:{}'.format(str(e2)))
        return json_custom_response(errors_occured=[{'message': 'Remove error'}], code=500)

    try:
        shell_cmd('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'private', unique_client_name + '.key')))
        shell_cmd('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'issued', unique_client_name + '.crt')))
        shell_cmd('rm {} -f'.format(os.path.join(cluster_easy_rsa_path, 'pki', 'reqs', unique_client_name + '.req')))
    except Exception as e:
        logging.getLogger(__file__).error('Error during client {} remove:{}'.format(unique_client_name, str(e)))
        return json_custom_response(errors_occured=[{'message': 'Remove error'}], code=500)

    return json_custom_response(
        data={
            'message': 'Removed',
            'client_name': unique_client_name,
        },
        code=200
    )


@openvpn_client_bp.route("/load/<unique_client_name>", methods=['POST'])
@auth_required
def load_client(unique_client_name):
    """Загружает ovpn клиента"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')

    body = request.get_json()
    key = body.get('data', {}).get('client_key', '')
    crt = body.get('data', {}).get('client_crt', '')
    req = body.get('data', {}).get('client_req', '')
    is_revoked = body.get('data', {}).get('is_revoked', True)

    # если сертификат уже загружен - проверяем что контент файла и запроса совпадают, если клиента еще нет- загружаем
    client_crt_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if os.path.exists(client_crt_path):
        f = open(client_crt_path, 'r')
        data = f.read()
        f.close()
        if re.findall('\w\d', data) != re.findall('\w\d', crt):
            return json_custom_response(errors_occured=[{'message': 'Different client already exists'}], code=400)
    else:
        try:
            shell_cmd('echo "{}" > {}'.format(key, os.path.join(cluster_easy_rsa_path, 'pki', 'private', unique_client_name + '.key')))
            shell_cmd('echo "{}" > {}'.format(crt, os.path.join(cluster_easy_rsa_path, 'pki', 'issued', unique_client_name + '.crt')))
            shell_cmd('echo "{}" > {}'.format(req, os.path.join(cluster_easy_rsa_path, 'pki', 'reqs', unique_client_name + '.req')))
        except Exception as e:
            logging.getLogger(__file__).error('Error during client {} load:{}'.format(unique_client_name, str(e)))
            return json_custom_response(errors_occured=[{'message': 'Load error'}], code=500)

    # обновляем index.txt
    try:
        index_txt_path = os.path.join(cluster_easy_rsa_path, 'pki', 'index.txt')
        index_txt_content = ''
        with open(index_txt_path, 'r+') as f:
            index_txt_content = f.read()
            f.truncate()
        record_in_index_txt = re.findall(
            '[R|V].{1,10}\d{1,12}.{1,700}CN=' + str(unique_client_name) + '.{0,150}\n',
            index_txt_content
        )

        # если в index.txt уже есть сертифкат
        if len(record_in_index_txt) > 0:
            with open(index_txt_path, 'w') as f:
                index_txt_content = index_txt_content.replace(record_in_index_txt[0], '')
                f.write(index_txt_content)
                f.truncate()

        # если нет - добавляем новую запись в index.txt
        crt_fp = os.path.join(cluster_easy_rsa_path, 'pki', 'issued', unique_client_name + '.crt')

        raw_serial = shell_cmd('''openssl x509 -in "{}" -noout -serial'''.format(crt_fp), capture=True)
        serial = raw_serial.replace('serial=', '')

        raw_dn = shell_cmd('''openssl x509 -in "{}"  -noout -subject -nameopt sep_multiline'''.format(crt_fp), capture=True)
        dn = '/{}'.format('/'.join(filter(lambda x: 'subject' not in x.lower(), re.findall(r'\w{1,20}=.{0,100}', raw_dn))))

        raw_expired_date = shell_cmd('''openssl x509 -in "{}" -noout -enddate'''.format(crt_fp), capture=True)
        raw_expired_date = raw_expired_date.lower().replace('notafter=', '').replace(' ', '').replace('gmt', '')
        try:
            expired_date = datetime.strptime(raw_expired_date, '%b%d%H:%M:%S%Y')
        except Exception:
            # для опенвна иметь 31 день в феврале норма, по этому если конвертация по дефолту не удается
            # меняем число на 25 и пытаемся конвертировать еще раз
            month = raw_expired_date[:3]
            day = raw_expired_date[3:5]
            raw_expired_date = raw_expired_date.replace('{}{}'.format(month, day), '{}25'.format(month))
            expired_date = datetime.strptime(raw_expired_date, '%b%d%H:%M:%S%Y')

        expired_date = '{}Z'.format(expired_date.strftime('%y%m%d%H%M%S'))

        if is_revoked:
            revoked_date = '{}Z'.format(datetime.utcnow().strftime('%y%m%d%H%M%S'))
            record = 'R\t{}\t{}\t{}\tunknown\t{}\r\n'.format(expired_date, revoked_date, serial, dn)
        else:
            record = 'V\t{}\t\t{}\tunknown\t{}\r\n'.format(expired_date, serial, dn)

        f = open(index_txt_path, 'a')
        f.write(record)
        f.close()

        shell_cmd('chmod 775 {}'.format(index_txt_path))
        shell_cmd('timeout 5 bash -c "cd {} && ./easyrsa gen-crl"'.format(cluster_easy_rsa_path))
        shell_cmd('cd {} && chmod 775 crl.pem'.format(os.path.join(cluster_easy_rsa_path, 'pki')))

    except Exception as e:
        logging.getLogger(__file__).error('Error during update index.txt. error:{}'.format(str(e)))
        return json_custom_response(errors_occured=[{'message': 'Load error'}], code=500)

    return json_custom_response(
        data={
            'message': 'Loaded',
            'client_name': unique_client_name,
        },
        code=200
    )


@openvpn_client_bp.route("/restore/<unique_client_name>", methods=['POST'])
@auth_required
def restore_client(unique_client_name):
    """
    Восстанавливает доступ ovpn клиенту,
    Для того чтобы отменить отзыв сертификата - сертификат нужно сначала положить на сервер
    """
    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    client_crt_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa/pki/issued', '{}.crt'.format(unique_client_name))
    if not os.path.exists(client_crt_path):
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')
    index_txt_path = os.path.join(cluster_easy_rsa_path, 'pki', 'index.txt')

    try:
        index_txt_content = ''
        with open(index_txt_path, 'r+') as f:
            index_txt_content = f.read()
            f.truncate()

        revoked_client_string = re.findall('[R].{1,10}\d{1,12}.{1,700}CN=' + str(unique_client_name) + '.{0,150}\n', index_txt_content)
        if len(revoked_client_string) != 1:
            return json_custom_response(errors_occured=[{'message': 'Client for restore not found'}], code=400)
        revoked_client_string = str(revoked_client_string[0])
        restored_client_string = \
            'V\t{}\t\t{}\t{}\t{}\r\n'.format(
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

        shell_cmd('chmod 775 {}'.format(index_txt_path))
        shell_cmd('timeout 5 bash -c "cd {} && ./easyrsa gen-crl"'.format(cluster_easy_rsa_path))
        shell_cmd('cd {} && chmod 775 crl.pem'.format(os.path.join(cluster_easy_rsa_path, 'pki')))
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


@openvpn_client_bp.route("/kick/<unique_client_name>", methods=['POST'])
@auth_required
def kick_client(unique_client_name):
    """Отключает пользователья от сервера"""

    unique_client_name = str(unique_client_name)
    if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
        return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

    output = ''
    output_tmp_file_name = os.path.join(
        settings.TMP_OUTPUT_DIR,
        'tmp_kill_{}_output_{}.txt'.format(unique_client_name, str(uuid.uuid4()))

    )
    cmd = """timeout 7 bash -c 'HOST="{0}" && CMD="kill {1}" && (echo open "$HOST" && sleep 2 && echo "$CMD" && sleep 2 && echo "exit") | telnet' > {2}""".format(
        settings.OPENVPN_TELNET_MANAGEMENT,
        unique_client_name,
        output_tmp_file_name
    )

    try:
        try:
            # Эта штука работает, но всегда падает из-за exit и timeout по этому выхлоп вытягивается через файл
            shell_cmd(cmd, no_logs=True)
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
        logging.getLogger(__file__).error('Error during kill {}:{}'.format(output_tmp_file_name, str(e1)))
        return json_custom_response(
            errors_occured=[{'message': 'Kick error', 'Internal error': str(e1)}],
            code=500
        )
    finally:
        try:
            os.remove(output_tmp_file_name)
        except Exception as e2:
            logging.getLogger(__file__).error('Error during remove {}:{}'.format(output_tmp_file_name, str(e2)))


@openvpn_client_bp.route("/get/<unique_client_name>", methods=['POST'])
@auth_required
def get_client(unique_client_name):
    """Возвращает ovpn клиента"""
    try:
        unique_client_name = str(unique_client_name)
        if unique_client_name.lower() in settings.IGNORED_CLIENT_NAMES:
            return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

        cluster_easy_rsa_path = os.path.join(settings.OPENVPN_PATH, 'easy-rsa')
        server_ca_path = os.path.join(cluster_easy_rsa_path, 'pki/ca.crt')
        server_ta_key_path = os.path.join(cluster_easy_rsa_path, 'pki/ta.key')

        client_common_path = os.path.join(settings.OPENVPN_PATH, 'client-common.txt')
        client_crt_path = os.path.join(cluster_easy_rsa_path, 'pki/issued/{}.crt'.format(unique_client_name))
        client_key_path = os.path.join(cluster_easy_rsa_path, 'pki/private/{}.key'.format(unique_client_name))
        client_req_path = os.path.join(cluster_easy_rsa_path, 'pki/reqs/{}.req'.format(unique_client_name))

        if not os.path.exists(client_crt_path):
            return json_custom_response(errors_occured=[{'message': 'Client not found'}], code=400)

        is_revoked = None
        index_txt_path = os.path.join(cluster_easy_rsa_path, 'pki', 'index.txt')
        index_txt_content = ''
        with open(index_txt_path, 'r+') as f:
            index_txt_content = f.read()
            f.truncate()
        record_in_index_txt = re.findall(
            '[R|V].{1,10}\d{1,12}.{1,700}CN=' + str(unique_client_name) + '.{0,150}\n',
            index_txt_content
        )
        try:
            if str(record_in_index_txt[0][0]).upper() == 'R':
                is_revoked = True
            elif str(record_in_index_txt[0][0]).upper() == 'V':
                is_revoked = False
        except Exception as e:
            logging.getLogger(__file__).error(
                'Error occured during getting client status. Error:{}. Client:{}, index.txt record:{}'.format(
                    str(e),
                    str(unique_client_name),
                    str(record_in_index_txt)
                )
            )

        return json_custom_response(
            data={
                'client_key': open(client_key_path, 'r').read(),
                'client_crt': open(client_crt_path, 'r').read(),
                'client_req': open(client_req_path, 'r').read(),
                'server_ca': open(server_ca_path, 'r').read(),
                'server_ta_key': open(server_ta_key_path, 'r').read(),
                'client_common': open(client_common_path, 'r').read(),
                'client_name': unique_client_name,
                'is_revoked': is_revoked
            },
            code=200
        )
    except Exception as e:
        logging.getLogger(__file__).error('Client get error. unique_client_name:{}. Error:{}'.format(
            str(unique_client_name),
            str(e)
        ))
        return json_custom_response(errors_occured=[{'message': 'An error occured during client getting'}], code=500)
