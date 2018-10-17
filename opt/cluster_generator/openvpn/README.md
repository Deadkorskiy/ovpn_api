
# Генерация файлов /etc/openvpn для нвого кластера и создание нового кластера

Вся генерация выполняется файлом `openvpn-install.sh`. 

В нем настраиваются:
- ip сервера. Будет использован в client-common **По умолчанию 0.0.0.0 надо менять самому в сгенерированых файлах**
- порт сервера используется в server.conf и client-common **По умолчанию 1194, менять не надо настраивается\мапится в docker-compose.yml**
- переменые vars которые использует easy-rsa для создания сертификатов. (данные в сертификате о компании, регионе, мыле админа и т.д.)
- DNS которые будут использовать клиенты server.conf
- telnet managment port

Из папки  `onetimevpn_openvpn/opt/cluster_generator/openvpn` запускаем :

`docker-compose build && docker-compose run openvpn --rm && mv openvpn cluster_openvpn`

- создаст в папке `cluster_generator/openvpn` папку `cluster_openvpn` в 
которой будет все для нового кластера (`/etc/openvpn`)

- Если по каким то причинам в папке `cluster_generator/openvpn` есть папка `openvpn` - ее надо удалить, 
Иначе при повтороном запуске, новый кластер не создатся. 

- Новый openvpn создается слушает адресс 0.0.0.0 и порт 1194. Порт мапится на уровне docker compose, а вот ip 
 лучше поменять в client-comman. Правим `cluster_openvpn/server.conf`, `cluster_openvpn/client-common.txt`, делаем подписи.

- Переносим папку `cluster_openvpn` в `onetimevpn_vpn/opt/deploy/docker/files/staging/vpn/openvpn/<YOUT_CLUSTER_NAME>/<openvpn>`

- добавляем новые хосты серверов в `inventories`

- чтобы запустить подготовленный кластер (только для первого раза) 
`docker-compose up --build -d` потом только `docker-compose  start|stop|restart`

