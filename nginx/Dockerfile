FROM nginx

RUN mkdir /static && mkdir /static/tiff && mkdir /static/images

ADD nginx.conf /etc/nginx/nginx.conf
ADD .htpasswd /etc/nginx/.htpasswd

EXPOSE 80 443
