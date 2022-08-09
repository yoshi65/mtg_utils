#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import pandas as pd
from classopt import ClassOpt, config


class Opt(ClassOpt):
    line: int = config(default=30, long=True, short=True)


def main(opt: Opt):
    pd.set_option('display.max_rows', None)
    name = 'both_name'
    price = 'Prices'
    columns = [name, price]

    resource = boto3.resource('dynamodb')
    table = resource.Table('mtg_prices')
    data = table.scan()

    price_table = pd.DataFrame([], columns=columns)

    for item in data['Items']:
        if item['Name'] != 'Total price' and item['Number'] > 0:
            p = item[price][max(item[price])]
            price_table = pd.concat([price_table, pd.DataFrame({name: [item[name]], price: [p]})])

    price_table.sort_values(by=price, inplace=True, ascending=False)
    price_table.reset_index(inplace=True, drop=True)

    for n in range(opt.line if opt.line != 0 else len(price_table)):
        line = price_table.iloc[n]
        print(f'{str(n+1): >3}{line[price]: >7}   {line[name]: <100}')


if __name__ == "__main__":
    opt = Opt.from_args()
    main(opt)
