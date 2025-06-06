#!/bin/sh

CERT_DIR="certs"
KEY_FILE="${CERT_DIR}/key.pem"
CERT_FILE="${CERT_DIR}/cert.pem"

mkdir -p "$CERT_DIR"

if [ ! -f "$KEY_FILE" ] || [ ! -f "$CERT_FILE" ]; then
    echo "[TLS] Generating self-signed certificate..."
    openssl req -newkey rsa:2048 -nodes \
        -keyout "$KEY_FILE" \
        -x509 -days 365 \
        -out "$CERT_FILE" \
        -subj "/C=US/ST=None/L=None/O=Synapse/CN=localhost"
else
    echo "[TLS] Certs already exist. Skipping generation."
fi
