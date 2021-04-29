#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	lambda_function
# CreatedDate:  2021-04-27 20:41:27 +0900
# LastModified: 2021-04-28 14:33:02 +0900
#


import json
import boto3
import logging
from os import getenv
import requests
import time
from urllib.parse import parse_qs

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    table_name = getenv('table_name')
    logger.info(f"table_name: {table_name}")

    name = parse_qs(event['body-json'])['text'][0].rstrip()
    logger.info(f"name: {name}")

    resource = boto3.resource('dynamodb')
    table = resource.Table(table_name)

    url = generate_url(name)

    if is_correct_url(name, url):
        insert_card_info(table, name, url)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Successfully insert {name} to {table_name}", }),
        }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"Fail to insert {name} to {table_name} because generated url is not correct",
            }),
        }


def generate_url(name: str) -> str:
    address = 'http://wonder.wisdom-guild.net/price'
    tranlated_name = translate_name(name)
    url = f'{address}/{tranlated_name}/'

    logger.info(f"generated url: {url}")
    return url


def translate_name(name: str) -> str:
    """Not complete func"""
    return name.replace(' ', '+').replace(',', '%2C')


def insert_card_info(table, name: str, url: str) -> None:
    table.put_item(
        Item={
            'Name': name,
            'URL': url,
            'Prices': dict()
        }
    )


def is_correct_url(name: str, url: str) -> bool:
    site = requests.get(url)
    time.sleep(1)

    return name in site.text
