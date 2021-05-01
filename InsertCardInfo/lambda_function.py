#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	lambda_function
# CreatedDate:  2021-04-27 20:41:27 +0900
# LastModified: 2021-05-01 12:52:54 +0900
#


import json
import boto3
from bs4 import BeautifulSoup
import logging
from os import getenv
import requests
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
    site = requests.get(url)
    both_name = get_both_name(site)  # ja_name/en_name

    if is_correct_url(name, site):
        insert_card_info(table, name, both_name, url)
        payload = {
            'attachments': [{
                'color': '#D3D3D3',
                'pretext': f'Inserted {both_name} to {table_name}',
            }]
        }
        post_slack(payload)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Successfully insert {both_name} to {table_name}", }),
        }
    else:
        payload = {
            'attachments': [{
                'color': '#EB3228',
                'pretext': f'Failed to insert {both_name} to {table_name}',
            }]
        }
        post_slack(payload)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"Fail to insert {both_name} to {table_name} because generated url is not correct",
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


def insert_card_info(table, name: str, both_name: str, url: str) -> None:
    table.put_item(
        Item={
            'Name': name,
            'URL': url,
            'both_name': both_name,
            'Prices': dict()
        }
    )


def is_correct_url(name: str, site) -> bool:
    return name in site.text


def get_both_name(site) -> str:
    data = BeautifulSoup(site.text, "html.parser")
    return data.select('h1.wg-title')[0].get_text()


def post_slack(payload):
    SLACK_WEBHOOK_URL = getenv('SLACK_WEBHOOK_URL')

    try:
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
