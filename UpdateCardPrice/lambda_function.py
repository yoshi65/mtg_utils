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
        if item['Name'] != 'Total price':
            price = get_price(item['URL'])
            if price:
                update_price(
                    table,
                    item['Name'],
                    datetime.now().strftime('%Y-%m-%d'),
                    price,
                )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Successfully update {table_name}",
        }),
    }


def update_price(table, card: str, date: str, price: int) -> None:
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

    if "wisdom" in url:
        price_str = data.select('div.wg-wonder-price-summary div.contents b')[1].get_text()
    elif "hareruya" in url:
        price_str = data.select("div.col-xs-3")[2].get_text().replace('￥', '')

    price = int(price_str.replace(",", ""))
    logger.info(f"get_price response: {url} -> {price}")
    time.sleep(0.5)

    return price if price != 99999 else None
