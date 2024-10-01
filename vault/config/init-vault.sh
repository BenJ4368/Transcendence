#!/bin/sh

CERTS_DIR=/vault/certs
mkdir -p $CERTS_DIR

if ! command -v openssl &> /dev/null
then
    echo "OpenSSL not found. Installing..."
    apk add --no-cache openssl
fi

if [ ! -f "$CERTS_DIR/vault.key" ] || [ ! -f "$CERTS_DIR/vault.crt" ]
then
    echo "Generating auto-signed TLS certificat..."
    openssl genrsa -out $CERTS_DIR/vault.key 2048
    openssl req -new -x509 \
        -key $CERTS_DIR/vault.key \
        -out $CERTS_DIR/vault.crt -days 365 \
        -subj "/C=FR/ST=Mulhouse/L=Mulhouse/O=ft_transcendence/CN=vault"
fi

vault server -config=/vault/config/vault-config.hcl
