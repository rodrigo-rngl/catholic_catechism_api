#!/bin/sh
set -e

envsubst '$DOMAIN' \
  < /etc/nginx/nginx-http-only.conf.template \
  > /etc/nginx/nginx.conf

envsubst '$DOMAIN' \
  < /etc/nginx/nginx-https-final.conf.template \
  > /etc/nginx/nginx-https-final.conf

exec nginx -g 'daemon off;'