FROM ubuntu:latest

RUN apt update && apt upgrade -y

RUN apt install -y \
    python3-pip \
    python3-dev

RUN cd /usr/local/bin && ln -s /usr/bin/python3 python

RUN pip3 install --upgrade pip

RUN mkdir /src && mkdir /src/DataCollector && cd /src/DataCollector

ADD requirements.txt /src/DataCollector/requirements.txt

RUN cd /src/DataCollector && pip3 install -r requirements.txt

