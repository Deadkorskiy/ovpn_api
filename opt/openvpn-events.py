#!/usr/bin/python3.6

# АЛЯРМ ПОМЕНЯТЬ ЭНВ!
# НУЖНО ДАТЬ ПРАВА НА ИСПОЛНЕНИЕ
# НУЖНО СДЕЛАТЬ ИСПОЛНЯЕМЫМ chmod +x
import os
import datetime
import logging
import uuid
import json
from src.libs.db_gateway import get_db_gateway
from src.settings import settings
from enum import Enum

logger = logging.getLogger('openvpn_client_event')


class ClientConnectionEvent(object):

    class EventTypes(Enum):
        # подключился
        CONNECT = 'client-connect'
        # отключился (но только если graceful) при обрыве связи эвент может не сработать
        DISCONNECT = 'client-disconnect'
        # сервисные эвенты openvpn
        UP = 'up'
        DOWN = 'down'
        # Тестовый тип для запуска скрипта вне окружения OpenVPN
        TEST = 'test_type'

    def __init__(self):
        self.redis = get_db_gateway('redis')

    @staticmethod
    def get_client_info() -> dict:
        return {
            'server_id': settings.SERVER_ID,
            'cluster_id': settings.CLUSTER_ID,
            'action': os.getenv('script-type', None),
            'common_name': os.getenv('common_name', None),
            'ip': os.getenv('trusted_ip', None),
            'port': os.getenv('trusted_port', None),
            'lan_ip': os.getenv('ifconfig_pool_remote_ip', None),
            'platform': os.getenv('IV_PLAT', None),
            'timestamp': int(datetime.datetime.utcnow().timestamp()),
        }

    def handle(self):
        event_type = os.getenv('script_type', 'test_type')

        try:
            event_type = self.EventTypes(event_type)
        except ValueError:
            # Для дебага скрипта
            logging.warning('Wrong script type action')

        options = {
            'client-connect': self.on_connect,
            'client-disconnect': self.on_disconnect,
            'up': self.on_up,
            'down': self.on_down,
            'test_type': self.test_event
        }
        options[event_type.value]()

    def enqueue(self, data: dict):
        queue_uid = str(uuid.uuid4())
        action = data.get('action')
        queue_key_name = '{}_{}'.format(action, queue_uid)
        self.redis.set(queue_key_name, json.dumps(data).encode())

    # Разделил эвенты, чтоб в будущем можно было разные действия при разных
    # эвентах выполнять, если вдруг понадобится, а пока делаем одно и то же
    def on_connect(self):
        self.enqueue(self.get_client_info())

    def on_disconnect(self):
        self.enqueue(self.get_client_info())

    def on_up(self):
        pass

    def on_down(self):
        pass

    def test_event(self):
        # Тестовый эвент, для запуска скрипта вне опенвпн окружения
        self.enqueue(self.get_client_info())

if __name__ == '__main__':
    for _ in range(100):
        ClientConnectionEvent().handle()


"""
СПРАВОЧНИК ПЕРЕМЕННЫХ

>CLIENT:ESTABLISHED,77
>CLIENT:ENV,n_clients=1
>CLIENT:ENV,ifconfig_pool_netmask=255.255.255.0
>CLIENT:ENV,ifconfig_pool_remote_ip=10.8.0.21
>CLIENT:ENV,script_type=client-connect
>CLIENT:ENV,time_unix=1550164029
>CLIENT:ENV,time_ascii=Thu Feb 14 17:07:09 2019
>CLIENT:ENV,trusted_port=52339
>CLIENT:ENV,trusted_ip=5.228.22.139
>CLIENT:ENV,common_name=844cecbf-5d7c-41b4-846c-5cc407b6f954
>CLIENT:ENV,IV_PROTO=2
>CLIENT:ENV,IV_PLAT=mac
>CLIENT:ENV,IV_VER=2.3.17
>CLIENT:ENV,untrusted_port=52339
>CLIENT:ENV,untrusted_ip=1.1.1.1
>CLIENT:ENV,tls_serial_hex_0=1a:a3:55:1d:10:1e:2f:43:6c:4e:16:0a:d8:c3:fc:68
>CLIENT:ENV,tls_serial_0=35407998585770264031291987424910244968
>CLIENT:ENV,tls_digest_sha256_0=53:45:48:15:45:2d:b8:a8:c0:bd:d8:24:82:92:b3:5a:58:b1:cb:14:95:31:94:f3:16:58:6c:2a:b4:ac:78:88
>CLIENT:ENV,tls_digest_0=0e:3e:ff:ea:2f:d9:6e:62:81:6e:0f:4a:b6:f4:db:5a:f2:91:79:41
>CLIENT:ENV,tls_id_0=C=PA, ST=PANAMA, L=PANAMA, O=OneTimeVPN, OU=OneTimeVPN, CN=844cecbf-5d7c-41b4-846c-5cc407b6f954, emailAddress=ca@onetimevpn.com
>CLIENT:ENV,X509_0_emailAddress=ca@onetimevpn.com
>CLIENT:ENV,X509_0_CN=844cecbf-5d7c-41b4-846c-5cc407b6f954
>CLIENT:ENV,X509_0_OU=OneTimeVPN
>CLIENT:ENV,X509_0_O=OneTimeVPN
>CLIENT:ENV,X509_0_L=PANAMA
>CLIENT:ENV,X509_0_ST=PANAMA
>CLIENT:ENV,X509_0_C=PA
>CLIENT:ENV,tls_serial_hex_1=93:30:35:9c:0e:36:89:59
>CLIENT:ENV,tls_serial_1=10606036066827143513
>CLIENT:ENV,tls_digest_sha256_1=8f:4a:56:34:42:b3:22:b4:5a:e4:76:75:dd:d6:b1:14:65:0c:33:3b:3a:80:c9:51:ba:35:7b:b5:d0:13:d2:34
>CLIENT:ENV,tls_digest_1=42:fd:34:25:27:22:0b:71:fb:04:b6:95:18:79:05:e0:aa:75:7c:88
>CLIENT:ENV,tls_id_1=C=PA, ST=PANAMA, L=PANAMA, O=OneTimeVPN, OU=OneTimeVPN, CN=ChangeMe, emailAddress=ca@onetimevpn.com
>CLIENT:ENV,X509_1_emailAddress=ca@onetimevpn.com
>CLIENT:ENV,X509_1_CN=ChangeMe
>CLIENT:ENV,X509_1_OU=OneTimeVPN
>CLIENT:ENV,X509_1_O=OneTimeVPN
>CLIENT:ENV,X509_1_L=PANAMA
>CLIENT:ENV,X509_1_ST=PANAMA
>CLIENT:ENV,X509_1_C=PA
>CLIENT:ENV,remote_port_1=443
>CLIENT:ENV,local_port_1=443
>CLIENT:ENV,proto_1=tcp-server
>CLIENT:ENV,daemon_pid=24935
>CLIENT:ENV,daemon_start_time=1550091461
>CLIENT:ENV,daemon_log_redirect=0
>CLIENT:ENV,daemon=1
>CLIENT:ENV,verb=3
>CLIENT:ENV,config=/etc/openvpn/server.conf
>CLIENT:ENV,ifconfig_local=10.8.0.1
>CLIENT:ENV,ifconfig_netmask=255.255.255.0
>CLIENT:ENV,ifconfig_broadcast=10.8.0.255
>CLIENT:ENV,script_context=init
>CLIENT:ENV,tun_mtu=1500
>CLIENT:ENV,link_mtu=1624
>CLIENT:ENV,dev=tun0
>CLIENT:ENV,dev_type=tun
>CLIENT:ENV,redirect_gateway=0
>CLIENT:ENV,END
"""