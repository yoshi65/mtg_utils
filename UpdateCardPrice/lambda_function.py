#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	lambda_function
# CreatedDate:  2021-04-27 20:41:27 +0900 LastModified: 2021-04-28 08:46:39 +0900
#


import json
import boto3
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from os import getenv
import requests
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    table_name = getenv('table_name')
    logger.info(f"table_name: {table_name}")

    resource = boto3.resource('dynamodb')
    table = resource.Table(table_name)

    data = table.scan()

    for item in data['Items']:
        logger.info(f"item: {item}")
        update_price(
            table,
            item['Name'],
            datetime.now().strftime('%Y-%m-%d'),
            get_price(item['URL']),
        )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Successfully update {table_name}",
        }),
    }


def update_price(table, card: str, date: str, price: str) -> None:
    response = table.update_item(
        Key={
            'Name': card
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

    logger.info(f"add_price response: {response}")


def get_price(url: str) -> str:
    site = requests.get(url)
    data = BeautifulSoup(site.text, "html.parser")
    price = data.select('div.wg-wonder-price-summary div.contents b')[1].get_text()
    logger.info(f"get_price response: {url} -> {price}")
    time.sleep(1)

    return price
