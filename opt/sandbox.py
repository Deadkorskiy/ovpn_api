from src.libs.db_gateway import get_db_gateway
import requests
import json
from requests.auth import HTTPBasicAuth
from src.settings import settings
import uuid


def consume_openvpn_events_queue():
    redis = get_db_gateway('redis')
    # На данный момент сканим все ключи имеющиеся в хранилище
    # можно использовать специальный пэкэдж для очереди
    for key in redis.scan_iter():
        data = redis.get(key)
        json_data = json.loads(data)

        try:
            r = requests.post(
                settings.VPNMANAGER_API_URL,
                json={
                    "method": "service.openvpn_action",
                    "id": str(uuid.uuid4()),
                    "params": {
                        "event": json_data
                    }
                },
                verify=False,
                auth=HTTPBasicAuth(
                    settings.VPNMANAGER_LOGIN,
                    settings.VPNMANGER_PASSWORD
                )
            )

            r.raise_for_status()
            redis.delete(key)
        except Exception as e:
            # При неудачном реквесте не удаляем из очереди
            # достанем по ключу в след включение селери
            pass
