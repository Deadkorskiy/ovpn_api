FROM ubuntu:18.04

RUN apt-get update -y  --fix-missing

# OPENVPN
RUN apt-get install -y openvpn iptables openssl ca-certificates
ADD etc/openvpn/start.sh start.sh
RUN ["chmod", "+x", "/start.sh"]

# API
RUN apt-get install -y software-properties-common
RUN apt-get install -y ssh telnet build-essential libssl-dev python3.6 python3.6-dev python3-pip python3.6-venv
# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel
RUN mkdir /code/src /code/etc /code/var -p;
ADD etc/ /code/etc
RUN python3.6 -m pip install -r /code/etc/requirements.txt

#NGINX
RUN apt-get install -y nginx
ADD etc/nginx.conf /etc/nginx/nginx.conf

# LAUNCHING
RUN apt-get install -y supervisor
ADD etc/openvpn/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir -p /var/log/supervisord && touch /var/log/supervisord/supervisord.log
ENTRYPOINT ["/usr/bin/supervisord"]