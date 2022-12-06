import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("焼肉キング戦いの記録")."2022/11/17"

# Extract and print all of the values
list_of_hashes = sheet.get_all_records()
print(list_of_hashes)

def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return: 
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

def paste_to_spreadsheet(paste_list):


response_for_tanpin_tag = requests.get("https://www.yakiniku-king.jp/menu_all/tanpin/")
all_tanpin_tag = BeautifulSoup(response_for_tanpin_tag.content, 'html.parser').select('a[href*="menu_all/tanpin"]')
all_href_list = list(map(lambda x: "https://www.yakiniku-king.jp" + x.get('href'), all_tanpin_tag))
tanpin_tag_href_list = list(filter(lambda x: not x.replace("/","").endswith("tanpin"), all_href_list))
# print(tanpin_tag_href_list)
# item_name_list = []
# for url in tanpin_tag_href_list:
#     time.sleep(0.5)
#     r = requests.get("https://www.yakiniku-king.jp/menu_all/tanpin/domestic_beef/")
#     soup = BeautifulSoup(r.content, 'html.parser')
#     item_name_list.extend(list(split_list(list(map(lambda x: x.text, soup.select("div.item_description h2, div.item_description span"))),3)))
# print(item_name_list)
response_for_kikan_gentei = requests.get("https://www.yakiniku-king.jp/menu_all/season/")
all_kikan_gentei = BeautifulSoup(response_for_kikan_gentei.content, 'html.parser').select('a[href*="menu_all/season"]')
all_href_list_kikan_gentei = list(set(list(map(lambda x: "https://www.yakiniku-king.jp" + x.get('href'), all_kikan_gentei))))
kikan_gentei_tag_href_list = list(filter(lambda x: not x.replace("/","").endswith("season"), all_href_list_kikan_gentei))
print(kikan_gentei_tag_href_list)

