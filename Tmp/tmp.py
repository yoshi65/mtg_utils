#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	tmp
# CreatedDate:  2021-05-16 15:44:46 +0900
# LastModified: 2021-05-16 15:46:09 +0900
#

import requests
from bs4 import BeautifulSoup


url = "https://www.hareruyamtg.com/ja/products/detail/69767?lang=EN"
site = requests.get(url)
data = BeautifulSoup(site.text, "html.parser")
title = data.select("title")[0].get_text().split('|')[0]
price = data.select("div.col-xs-3")[2].get_text().replace('￥', '')
print(f'{title}: {price}')
