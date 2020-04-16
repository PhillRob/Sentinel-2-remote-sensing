FROM ubuntu:latest

RUN apt update && apt upgrade -y
RUN apt install -y software-properties-common
RUN apt-add-repository -y ppa:nginx/stable
RUN apt update 
RUN apt install -y nginx

EXPOSE [80, 443]

RUN service nginx restart


