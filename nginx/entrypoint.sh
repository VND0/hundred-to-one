#!/bin/sh
# wait for certbot to resolve
until getent hosts certbot; do
  echo "Waiting for certbot..."
  sleep 1
done

nginx -g 'daemon off;'