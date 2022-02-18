#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	draw_total_price_timelapse
# CreatedDate:  2022-02-11 8:00:00 +0900
# LastModified: 2022-02-18 19:39:58 +0900
#


import boto3
import logging
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main():
    resource = boto3.resource('dynamodb')
    table = resource.Table('mtg_prices')
    data = table.scan()

    price_table = pd.DataFrame()

    for item in data['Items']:
        logger.info(f"item: {item}")
        if item['Name'] == 'Total price':
            price_table = pd.Series(item['Prices'], dtype=int)
            break

    price_table.sort_index(inplace=True)

    plt.figure(figsize=(8, 6))
    price_table.plot()
    plt.xticks(rotation=60)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Total price [yen]', fontsize=12)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig('totalprice_timelapse.png')

    return {
        "statusCode": 200,
    }


if __name__ == "__main__":
    main()
