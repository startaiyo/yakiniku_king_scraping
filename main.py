import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return: 
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

response_for_tanpin_tag = requests.get("https://www.yakiniku-king.jp/menu_all/tanpin/")
all_tanpin_tag = BeautifulSoup(response_for_tanpin_tag.content, 'html.parser').select('a[href*="menu_all/tanpin"]')
all_href_list = list(map(lambda x: "https://www.yakiniku-king.jp" + x.get('href'), all_tanpin_tag))
tanpin_tag_href_list = list(filter(lambda x: not x.replace("/","").endswith("tanpin"), all_href_list))
# print(tanpin_tag_href_list)
item_name_list = []
for url in tanpin_tag_href_list:
    time.sleep(0.5)
    r = requests.get("https://www.yakiniku-king.jp/menu_all/tanpin/domestic_beef/")
    soup = BeautifulSoup(r.content, 'html.parser')
    item_name_list.extend(list(split_list(list(map(lambda x: x.text, soup.select("div.item_description h2, div.item_description span"))),3)))
print(item_name_list)

