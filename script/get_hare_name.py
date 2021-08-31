#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: 	get_hare_name
# CreatedDate:  2021-05-16 15:44:46 +0900
# LastModified: 2021-08-31 19:09:06 +0900
#

import sys
import requests
from bs4 import BeautifulSoup


url = sys.argv[1]
site = requests.get(url)
data = BeautifulSoup(site.text, "html.parser")
title = data.select("title")[0].get_text().split('|')[0]
price = data.select("div.col-xs-3")[2].get_text().replace('￥', '')
print(f'{title}: {price}')
