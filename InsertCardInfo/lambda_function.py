#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	lambda_function
# CreatedDate:  2021-04-27 20:41:27 +0900
# LastModified: 2021-09-03 17:55:25 +0900
#


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

    name, num = get_name_num(parse_qs(event['body-json'])['text'][0].rstrip())
    logger.info(f"name: {name}")
    logger.info(f"num: {num}")

    resource = boto3.resource('dynamodb')
    table = resource.Table(table_name)

    url = generate_url(name)
    site = requests.get(url)

    if is_correct_url(name, site):
        both_name = get_both_name(site)  # ja_name/en_name
        insert_card_info(table, name, both_name, url, num)
        return {"text": f'Inserted {both_name} to {table_name}'}
    else:
        return {"text": f'{name} is not found'}


def get_name_num(text: str):
    split_text = text.rsplit(" ", 1)
    name = split_text[0]
    num = int(split_text[1])
    return name, num


def generate_url(name: str) -> str:
    address = 'http://wonder.wisdom-guild.net/price'
    tranlated_name = translate_name(name)
    url = f'{address}/{tranlated_name}/'

    logger.info(f"generated url: {url}")
    return url


def translate_name(name: str) -> str:
    """Not complete func"""
    return name.replace(' ', '+').replace(',', '%2C').replace('’', "'")


def insert_card_info(table, name: str, both_name: str, url: str, num: int) -> None:
    table.put_item(
        Item={
            'Name': name,
            'URL': url,
            'both_name': both_name,
            'Prices': dict(),
            'Number': num,
            'Notify': False if num else True,
        }
    )


def is_correct_url(name: str, site) -> bool:
    return name in site.text


def get_both_name(site) -> str:
    data = BeautifulSoup(site.text, "html.parser")
    return data.select('h1.wg-title')[0].get_text()
