from src.celery.jobs.base import BaseJob
from src.libs.db_gateway import get_db_gateway
import requests
import json
from requests.auth import HTTPBasicAuth
from src.settings import settings
import uuid


class ProcessOpenVPNEvents(BaseJob):
    def __init__(
            self,
    ):
        super().__init__()
        self.db = get_db_gateway('redis')

    def do_work(self, *args, **kwargs):
        # На данный момент сканим все ключи имеющиеся в хранилище
        # можно использовать специальный пэкэдж для очереди
        for key in self.db.scan_iter():
            data = self.db.get(key)
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
                self.db.delete(key)
            except requests.HTTPError as e:
                # При неудачном реквесте не удаляем ключи из очереди
                # просто ниые не делаем
                # достанем по ключу в след включение селери
                pass
