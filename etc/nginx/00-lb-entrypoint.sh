#!/usr/bin/env bash

declare -A hosts
hosts[wordpress]=$WORDPRESS_HOST
hosts[redmine]=$REDMINE_HOST
hosts[wagtail]=$WAGTAIL_HOST

mkdir -p /etc/nginx/templates

for name in "${!hosts[@]}"; do
  host=${hosts[$name]}
  echo "Checking ${name} service..."
  if curl -s $host -I > /dev/null; then
    echo "Enable ${name} template..."
    sed "s/UPSTREAM/${name^^}/" /tmp/lb.conf.template > "/etc/nginx/templates/${name}.conf.template"
  fi
done
