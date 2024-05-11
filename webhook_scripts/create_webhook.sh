#!/bin/bash

BOT_TOKEN_VAR_NAME="BOT_TOKEN"
CLOUD_FUNCTION_LINK_VAR_NAME="CLOUD_FUNCTION_LINK"

BOT_TOKEN=$(grep "^$BOT_TOKEN_VAR_NAME=" .env | cut -d '=' -f2)
CLOUD_FUNCTION_LINK=$(grep "^$CLOUD_FUNCTION_LINK_VAR_NAME=" .env | cut -d '=' -f2)

if [ -z "$BOT_TOKEN" ]; then
  echo "$BOT_TOKEN_VAR_NAME not found in .env file"
fi

if [ -z "$CLOUD_FUNCTION_LINK" ]; then
  echo "$CLOUD_FUNCTION_LINK_VAR_NAME not found in .env file"
fi

BOT_TOKEN=$(echo "$BOT_TOKEN" | sed "s/'//g")
CLOUD_FUNCTION_LINK=$(echo "$CLOUD_FUNCTION_LINK" | sed "s/'//g")

URL="https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$CLOUD_FUNCTION_LINK"

curl -s -X POST $URL
