
# Генерация файлов /etc/openvpn для нвого кластера и создание нового кластера

Из папки  `onetimevpn_openvpn/opt/cluster_generator/openvpn` запускаем :

`docker-compose build && docker-compose run openvpn --rm && mv openvpn cluster_openvpn`

- создаст в папке `cluster_generator/openvpn` папку `cluster_openvpn` в 
которой будет все для нового кластера (`/etc/openvpn`)

- Если по каким то причинам в папке `cluster_generator/openvpn` есть папка `openvpn` - ее надо удалить, 
Иначе при повтороном запуске, новый кластер не создатся. 

- Правим `cluster_openvpn/server.conf`, `cluster_openvpn/client-common.txt` и прочее файлы, делаем подписи и т.д.

- Добавляем данные о кластере в mongo

- Добавляем данные о сервер(е/ах) в mongo

- Переносим папку `cluster_openvpn` в `onetimevpn_openvpn/opt/deploy/docker/files/staging/vpn/openvpn/<YOUT_CLUSTER_NAME>/<openvpn>`

- добавляем новые хосты серверов в `inventories`