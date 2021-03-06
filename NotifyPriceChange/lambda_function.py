#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	lambda_function
# CreatedDate:  2021-04-27 20:41:27 +0900 LastModified: 2021-05-02 16:15:20 +0900
#


import boto3
from datetime import datetime
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

    threshold = 10
    attachments = list()

    data = table.scan()

    for item in data['Items']:
        logger.info(f"item: {item}")
        result = get_diff_price(item)
        logger.info(f'result: {result}')

        if result and over_threshold(result["percentage"], threshold) and item['Notify']:
            attachments.append(generate_attachment(item['both_name'], result, threshold))

    post_slack({'attachments': attachments})

    day_of_week = datetime.now().strftime('%a')
    logger.info(f"day of week: {day_of_week}")

    if day_of_week == 'Mon':
        total_price = calc_total_price(data['Items'])
        str_total_price = '{:,}'.format(total_price)
        logger.info(f"total price: {str_total_price}")
        post_slack(generate_block(f'Current total price: {str_total_price}円'))
        update_total_price(
            table,
            datetime.now().strftime('%Y-%m-%d'),
            total_price
        )

    return {
        "statusCode": 200,
    }


def get_diff_price(item) -> dict:
    price = item['Prices']
    if len(price):
        start_price = int(price[min(price)])
        recent_price = int(price[max(price)])
        return {
            "percentage": 100 * (recent_price - start_price) / start_price,
            "start_price": start_price,
            "recent_price": recent_price
        }
    else:
        return {}


def over_threshold(percentage: float, threshold: int) -> bool:
    return abs(percentage) >= threshold


def generate_attachment(name: str, result: dict, threshold: int) -> dict:
    red = "#ff0000"
    blue = "#0000ff"

    return {
        'color': red if result["percentage"] >= threshold else blue,
        'pretext': f'{name} {result["percentage"]:.2f}%',
        'text': f'Price: {result["start_price"]} -> {result["recent_price"]}'
    }


def calc_total_price(items):
    total_price = 0
    for item in items:
        prices = [item['Prices'][key] for key in item['Prices'].keys()]
        if len(prices) != 0 and item['Name'] != 'Total price':
            total_price += prices[-1] * item['Number']
    return total_price


def generate_block(text: str) -> dict:
    return {"blocks": [{
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": text
            }}]}


def post_slack(payload):
    SLACK_WEBHOOK_URL = getenv('SLACK_WEBHOOK_URL')

    try:
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        logger.info(e)


def update_total_price(table, date: str, price: int) -> None:
    response = table.update_item(
        Key={
            'Name': 'Total price'
        },
        UpdateExpression="set Prices.#date=:p",
        ExpressionAttributeNames={
            '#date': date
        },
        ExpressionAttributeValues={
            ':p': price,
        },
        ReturnValues="UPDATED_NEW"
    )

    logger.info(f"add_total_price response: {response}")
