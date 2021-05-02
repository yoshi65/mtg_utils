#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	lambda_function
# CreatedDate:  2021-04-27 20:41:27 +0900
# LastModified: 2021-05-02 11:54:12 +0900
#


import boto3
import json
import logging
from os import getenv

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
        get_diff_price(item)
        return None

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Successfully update {table_name}",
        }),
    }


def get_diff_price(item) -> list:
    price = item['Price']
    logger.info(f"price: {price}")
