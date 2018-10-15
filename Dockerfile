FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update -y

RUN apt-get install -y ssh build-essential libssl-dev python3.6 python3.6-dev python3-pip python3.6-venv

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel
RUN mkdir /code/src /code/etc /code/var -p;
ADD etc/ /code/etc/
RUN python3.6 -m pip install -r /code/etc/requirements.txt
EXPOSE 5000

