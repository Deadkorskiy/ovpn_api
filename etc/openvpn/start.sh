#!/bin/sh

sed -i '/\<net.ipv4.ip_forward\>/c\net.ipv4.ip_forward=1' /etc/sysctl.conf
if ! grep -q "\<net.ipv4.ip_forward\>" /etc/sysctl.conf; then
    echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
fi

iptables -A INPUT -p UDP --dport 1194 -j ACCEPT
iptables -A INPUT -p TCP --dport 1194 -j ACCEPT
iptables -A INPUT -s 10.15.0.0/24 -j ACCEPT
iptables -A FORWARD -s 10.15.0.0/24 -j ACCEPT
iptables -A FORWARD -d 10.15.0.0/24 -j ACCEPT
iptables -t nat -A POSTROUTING -s 10.15.0.0/24 -j MASQUERADE

exec openvpn --config /etc/openvpn/server.conf