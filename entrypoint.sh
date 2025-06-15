#!/bin/sh

echo "[ENTRYPOINT] Generating certificates..."
./cert-gen.sh

echo "[ENTRYPOINT] Setting certificate permissions..."
chmod 644 certs/cert.pem 2>/dev/null || true
chmod 644 certs/key.pem 2>/dev/null || true

echo "[ENTRYPOINT] Starting application..."
exec "$@"
