#!/usr/bin/env bash
# Generate the EC key pair the Tesla Fleet API requires, and place the public
# key where Caddy/nginx will serve it from your domain.
set -euo pipefail

WELL_KNOWN="${WELL_KNOWN:-/var/www/tesla/.well-known/appspecific}"
PRIVATE_OUT="${PRIVATE_OUT:-$HOME/tesla-private-key.pem}"

mkdir -p "$WELL_KNOWN"

# prime256v1 (a.k.a. secp256r1 / P-256) is what Tesla expects.
openssl ecparam -name prime256v1 -genkey -noout -out "$PRIVATE_OUT"
openssl ec -in "$PRIVATE_OUT" -pubout -out "$WELL_KNOWN/com.tesla.3p.public-key.pem"

chmod 600 "$PRIVATE_OUT"
echo "Private key : $PRIVATE_OUT  (keep secret, never commit)"
echo "Public key  : $WELL_KNOWN/com.tesla.3p.public-key.pem"
echo
echo "Tesla must be able to fetch it at:"
echo "  https://<your-domain>/.well-known/appspecific/com.tesla.3p.public-key.pem"
