# mtg_utils

Lambda functions for mtg utils

## Insert card info

Insert card info to dynamoDB table based on card name sent by slack slash command.

## Update card price

Update card price to dynamoDB and daily invoked.

## Notify price change

Notify price change (threshold: 10%) to slack channel.

## Required secrets
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
- CONTAINER_REGISTRY_PATH: `https://{aws_account_id}.dkr.ecr.{region}.amazonaws.com`
- SLACK_WEBHOOK_URL
