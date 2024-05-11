#!/bin/bash

BOT_TOKEN_VAR_NAME="BOT_TOKEN"

BOT_TOKEN=$(grep "^$BOT_TOKEN_VAR_NAME=" .env | cut -d '=' -f2)

if [ -z "$BOT_TOKEN" ]; then
  echo "$BOT_TOKEN_VAR_NAME not found in .env file"
fi

BOT_TOKEN=$(echo "$BOT_TOKEN" | sed "s/'//g")

URL="https://api.telegram.org/bot$BOT_TOKEN/deleteWebhook"

curl -s -X POST $URL
