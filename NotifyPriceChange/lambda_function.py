#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	lambda_function
# CreatedDate:  2021-04-27 20:41:27 +0900 LastModified: 2021-05-02 16:15:20 +0900
#


import boto3
import json
import logging
from os import getenv
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    table_name = getenv('table_name')
    logger.info(f"table_name: {table_name}")

    resource = boto3.resource('dynamodb')
    table = resource.Table(table_name)

    threshold = 0
    attachments = list()

    data = table.scan()

    for item in data['Items']:
        logger.info(f"item: {item}")
        result = get_diff_price(item)
        logger.info(f'result: {result}')

        if over_threshold(result["percentage"], threshold):
            attachments.append(generate_attachment(item['both_name'], result, threshold))

    post_slack({'attachments': attachments})

    return {
        "statusCode": 200,
    }


def get_diff_price(item) -> dict:
    price = item['Prices']
    start_price = int(price[min(price)])
    recent_price = int(price[max(price)])
    return {
        "percentage": (recent_price - start_price) / start_price,
        "start_price": start_price,
        "recent_price": recent_price
    }


def over_threshold(percentage: float, threshold: int) -> bool:
    return abs(percentage) >= threshold


def generate_attachment(name: str, result: dict, threshold: int) -> dict:
    red = "#ff0000"
    blue = "#0000ff"

    return {
        'color': red if result["percentage"] > threshold else blue,
        'pretext': f'{name} {result["percentage"]}%',
        'text': f'Price: {result["start_price"]} -> {result["recent_price"]}'
    }


def post_slack(payload):
    SLACK_WEBHOOK_URL = getenv['SLACK_WEBHOOK_URL']

    try:
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        logger.info(e)
