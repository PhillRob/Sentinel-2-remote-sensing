FROM ubuntu:latest

RUN apt update && apt upgrade -y
RUN apt install -y software-properties-common
RUN apt-add-repository -y ppa:nginx/stable
RUN apt update 
RUN apt install -y nginx

ADD nginx.conf /etc/nginx/nginx.conf

RUN mkdir /nginxcontent

EXPOSE 80 443

