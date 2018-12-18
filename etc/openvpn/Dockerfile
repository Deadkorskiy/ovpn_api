FROM ubuntu:18.04

RUN apt-get update -y  --fix-missing

# API
RUN apt-get install -y software-properties-common
RUN apt-get install -y ssh telnet build-essential libssl-dev python3.6 python3.6-dev python3-pip python3.6-venv
# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel
RUN mkdir /code/src /code/etc /code/var -p;
ADD etc/ /code/etc
RUN python3.6 -m pip install -r /code/etc/requirements.txt
