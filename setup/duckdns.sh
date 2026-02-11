#!/bin/bash
# Updates DuckDNS with current IP
# Add to cron: */5 * * * * /opt/sms/setup/duckdns.sh >> /var/log/duckdns.log 2>&1
source /opt/sms/.env
curl -s "https://www.duckdns.org/update?domains=sms-problemli&token=${DUCK_TOKEN}&ip="
echo " $(date)"
