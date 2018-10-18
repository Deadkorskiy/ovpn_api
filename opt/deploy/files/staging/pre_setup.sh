#!/usr/bin/env bash

apt-get install python2.7 python3 -y

USER=deploy
ID_RSA_PUB="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPGj3wvxLE5RcEpYouekl2svPn/rdVO2iUHzwXe4a70jfK0eLUHYxmOkrUjzS9FpmYF577BX3urGqj3tnFHRKnPl0sr+vS6QVpOPKKNBjhGkt0MHfUtYhqpqCFPRyFLolTnSwbQh1VAUsYWqrlcNNJjRDM7T3wD2KZn7KveNAuxYL103csOEPMN7ZiS5jXR+Iyq7EP9roCce8ymim3uUSUnQSLdSUzXrhccIe6vvLyFspfIu+jj56yk2cmI/VYEFGKyR3Q2hYEzcXLa7OGxhvgxchTolWaqYFya4Hc0mr60fJ1fyuYRU8+g1NdvyinroXSCqxcpBizrYFPc9yWShUb deploy"
ID_RSA="-----BEGIN RSA PRIVATE KEY-----\n
MIIEpAIBAAKCAQEAzxo98L8SxOUXBKWKLnpJdrLz5/63VTtolB88F3uGu9I3ytHi\n
1B2MZjpK1I80vRaZmBee+wV97qxqo97ZxR0Spz5dLK/r0ukFaTjyijQY4RpLdDB3\n
1LWIaqaghT0chS6JU50sG0IdVQFLGFqq5XDTSY0QzO098A9imZ+yr3jQLsWC9dN3\n
LDhDzDe2YkuY10fiMquxD/a6AnHvMpopt7lElJ0Ei3UlM164XHCHur7y8hbKXyLv\n
o4+espNnJiP1WBBRiskd0NoWBM3Fy2uzhsYb4MXIU6JVmqmBcmuB3NJq+tHydX8r\n
mEVPPoNTXb8op66F0gqsXKQYs62BT3PclkoVGwIDAQABAoIBADnz6u9KWJM2VAmd\n
1RwKZjJMA0qhEWZNWIdScjtT+rDmM2yS7PlUR2x31WbDqAtdnp9bxMYTlFjMcI7o\n
lmG9L/IS1nnhxIjhYf0+zUf1Kh0bgY/C3FVucvz9IaAHKMrv6ce3DJeYGaMm2H+5\n
J2dK+iTzz4a4wINDmuDIOnU1xnO/mnRf8PLewZlLrnXbKgeyjzBmr6FTVioOBxt9\n
G6ugthxmzXRweq4XtBWKyqzJaSWknhN21pZoTgxv9JcDOQvT6yiAyrq6AIAjIN7v\n
h9FIfyvlQFeSMlBlESN269UcIEQ9b8BrrRF8W7jhduEaq3iGdJRlY0+TQwJV+pJh\n
CnNMZZECgYEA6VLCgH9iYCaw5Qe+OTi4EyIUZ0zXFJiHYAv/rrKYzMLWoPQxtUbP\n
mq/sF7PVatD+z9EP4DtQpidYObJBb+PY9vWt2wgtRGUfcBxhY3L7oSqLtDwHxi7z\n
N1ZT8tDzU4SqVLQYL/pQjhQDh/hDXWKMR6FNrwPB7Vcv4C7/vawM79kCgYEA4zsX\n
emJL/hW2usYkWFzKiYxFtZycPX69qerle1Swi7zhChSQLxM1AYrc9u+OnZkTy3um\n
O4sMTl6Pr9jeg5/lOzlTG988scRCdPrKu0YGsYnfSKM3pWX/VMf8fM0VP6Gg0zxS\n
dLKqbqYtGlQVJKKJX3iy8WmZR5Qlj7NWx9iRiBMCgYEAqJeXWXgyIl3ythtpNTmp\n
sJGQgrAAPa6VKy6gWqBMTrB+m6C3hlAbVJ/Hjbzw+hT3+jwLJ7BUbyrA0jfelrXh\n
oVkWfc0jwGb9V2n6aPy9m8/9UIeL6oUkUxj64dpf6DpVRY04aPqLWI5Xmtkl/AVo\n
bZ29Xzfs2c2FF41+V5RJaMkCgYAZiTmBOmy52CzZ3oyVFZB5Vrc6yqfQTV75Knmx\n
m3nfqlFL9bWiZLEvRDDC23cWhO5xjqrGxECUyhGxvFh9SEnVlwKc/kBu5dRmGw0P\n
cLYt24WpPxZw0v6Xw4W/bLi3lu1g78WAcdevaaNl8w8RN+biQMkzUh+0qJR0Cr50\n
5QSt2wKBgQDZ3L3Lmgr9mwZEO555oFnzT+j9HNWK4JmsRKm/445jrh9N47sVS27A\n
Hd8THQWWFACmsQKCLHFAB0jW7zOtEZM/sxX/QDXjA0vY7jICVEazwKU7+JXzSzIS\n
IrWZ2DV5aAtCJUX1ABw9llptexmy6wMzlYt+rQiJQf1haEYO6OLVRw==\n
-----END RSA PRIVATE KEY-----"

GENERATED_PASS=$(python3 -c "import crypt; print(str(crypt.crypt('aksdnv764VGGHS2636sFCrfcasasdfca', 'xxs324E')))")
useradd -m -p $GENERATED_PASS -s /bin/bash $USER
usermod -a -G sudo $USER
mkdir -p /home/$USER/.ssh/
chmod 700 /home/$USER/.ssh
touch /home/$USER/.ssh/authorized_keys
echo $ID_RSA_PUB >> /home/$USER/.ssh/authorized_keys
chmod 600 /home/$USER/.ssh/authorized_keys
echo -e $ID_RSA >> /home/$USER/.ssh/id_rsa
chmod 600 /home/$USER/.ssh/id_rsa
chown $USER:$USER /home/$USER/.ssh -R
rm -- "$0"
