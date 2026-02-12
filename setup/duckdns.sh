#!/bin/bash
# Updates DuckDNS with current IP
# Cron (root): * * * * * /opt/sms/setup/duckdns.sh 2>&1 | logger -t duckdns
# View logs: journalctl -t duckdns
source /opt/sms/.env
curl -s "https://www.duckdns.org/update?domains=sms-problemli&token=${DUCK_TOKEN}&ip="
echo " $(date)"
