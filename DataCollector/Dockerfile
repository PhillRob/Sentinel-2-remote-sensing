FROM ubuntu:latest

WORKDIR /src/DataCollector
ADD . /src/DataCollector

RUN apt update && \
    apt upgrade -y && \
    apt install -y python3-pip python3-dev wget && \
    cd /usr/local/bin && \
    ln -s /usr/bin/python3 python && \
    pip3 install --upgrade pip && \
    mkdir /static && \
    cd /src/DataCollector && \
    pip3 install -r requirements.txt

 
