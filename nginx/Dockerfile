FROM debian:bullseye

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
    build-essential \
    libpcre3 \
    libpcre3-dev \
    libpcre2-dev \
    libssl-dev \
    zlib1g-dev \
    wget \
    curl \
    gnupg2 \
    openssl

RUN wget https://nginx.org/download/nginx-1.24.0.tar.gz && \
    wget https://github.com/nbs-system/naxsi/archive/master.tar.gz && \
    tar -zxvf nginx-1.24.0.tar.gz && \
    tar -zxvf master.tar.gz && \
    cd nginx-1.24.0 && \
    ./configure --with-http_ssl_module --add-module=../naxsi-master/naxsi_src && \
    make && \
    make install

RUN mkdir -p /etc/nginx/ssl \
    && openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -nodes \
        -out /etc/nginx/ssl/transcendence.crt \
        -keyout /etc/nginx/ssl/transcendence.key \
        -subj "/C=FR/ST=MULHOUSE/L=MULHOUSE/O=42 School/OU=transcendence/CN=transcendence/"

EXPOSE 443

COPY nginx.conf /usr/local/nginx/conf/.
COPY naxsi.rules /usr/local/nginx/conf/.
COPY naxsi_core.rules /usr/local/nginx/conf/.

CMD ["/usr/local/nginx/sbin/nginx", "-g", "daemon off;"]