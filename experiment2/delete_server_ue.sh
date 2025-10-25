#!/bin/bash

echo "ue: $1"
echo "IP: $2"

serverIp=$(ps aux | grep "$1" | grep -v grep | grep -Eo 'http://([0-9]{1,3}\.){3}[0-9]{1,3}' | head -n 1 | cut -d/ -f3)

if [ -z "$serverIp" ]; then
  echo "❌ 無法在 ps aux 找到對應 IP"
  exit 1
fi

echo "✅ Server IP found: $serverIp"

./nr-binder "$2" curl -s -X POST "http://$serverIp:18080/delete_ue/$1"

echo ""