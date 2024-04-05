#!/bin/bash
rm -rf ./genius-yield-trading-bot-api-client
openapi-python-client generate --path ./bot-api.yaml
rm -rf client
mkdir client
mv ./genius-yield-trading-bot-api-client/genius_yield_trading_bot_api_client/* ./client/
rm -rf ./genius-yield-trading-bot-api-client
touch ./client/___GENERATED_CODE_DO_NOT_EDIT___