#!/usr/bin/env bash

rm -rf /etc/letsencrypt/live/certfolder*

certbot certonly --standalone --email "$DOMAIN_EMAIL" -d "$DOMAIN_URL" \
  --cert-name=certfolder --key-type rsa --agree-tos

rm -f /etc/nginx/cert.pem
rm -f /etc/nginx/key.pem

cp /etc/letsencrypt/live/certfolder*/fullchain.pem /etc/nginx/cert.pem
cp /etc/letsencrypt/live/certfolder*/privkey.pem /etc/nginx/key.pem
