FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get install openvpn iptables openssl ca-certificates -y

EXPOSE 1194
EXPOSE 443

COPY start.sh start.sh
RUN ["chmod", "+x", "/start.sh"]

COPY openvpn-install.sh openvpn-install.sh
RUN ["chmod", "+x", "/openvpn-install.sh"]

ENTRYPOINT ["/start.sh"]
