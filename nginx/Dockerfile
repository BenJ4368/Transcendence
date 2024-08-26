FROM debian:bullseye

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
    nginx \
    openssl \
&& mkdir /etc/nginx/ssl \
&& openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -nodes \
    -out /etc/nginx/ssl/transcendence.crt \
    -keyout /etc/nginx/ssl/transcendence.key \
    -subj "/C=FR/ST=MULHOUSE/L=MULHOUSE/O=42 School/OU=transcendence/CN=transcendence/"

EXPOSE 443

COPY nginx.conf /etc/nginx/.

CMD ["nginx", "-g", "daemon off;"]