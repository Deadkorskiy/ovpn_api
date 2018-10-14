FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get install iptables openssl ca-certificates curl -y

ENTRYPOINT ["/openvpn-install.sh"]

