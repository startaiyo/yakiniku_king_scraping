import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# use creds to create a client to interact with the Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
book = client.open("焼肉キング戦いの記録")
sheet = book.worksheet('2022/12/3')

# Extract and print all of the values
list_of_hashes = sheet.get_all_values()

def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return: 
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

def add_price_to_sheet(item_list):
    price_sheet = book.worksheet('値段リスト')
    price_sheet.clear()
    price_sheet.append_rows(item_list)

def add_record_to_new_sheet(record_list):
    DIFF_JST_FROM_UTC = 9
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
    now_for_title = now.strftime('%Y/%m/%d')
    book.add_worksheet(now_for_title, rows = 100, cols = 4)

response_for_tanpin_tag = requests.get("https://www.yakiniku-king.jp/menu_all/tanpin/")
all_tanpin_tag = BeautifulSoup(response_for_tanpin_tag.content, 'html.parser').select('a[href*="menu_all/tanpin"]')
all_href_list = list(map(lambda x: "https://www.yakiniku-king.jp" + x.get('href'), all_tanpin_tag))
tanpin_tag_href_list = list(filter(lambda x: not x.replace("/","").endswith("tanpin"), all_href_list))
item_name_list = []
for url in tanpin_tag_href_list:
    time.sleep(0.5)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for tag in soup.select("div.item_description h2 span"):
        tag.decompose()
    item_name_list.extend(list(split_list(list(map(lambda x: "".join(x.text.split()), soup.select("div.item_description h2, div.item_description span"))),3)))
response_for_kikan_gentei = requests.get("https://www.yakiniku-king.jp/menu_all/season/")
all_kikan_gentei = BeautifulSoup(response_for_kikan_gentei.content, 'html.parser').select('a[href*="menu_all/season"]')
all_href_list_kikan_gentei = list(set(list(map(lambda x: "https://www.yakiniku-king.jp" + x.get('href'), all_kikan_gentei))))
kikan_gentei_tag_href_list = list(filter(lambda x: not x.replace("/","").endswith("season"), all_href_list_kikan_gentei))
for url in kikan_gentei_tag_href_list:
    time.sleep(0.5)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    item_name_list.append(list(map(lambda x: "".join(x.text.split()), soup.select("div.menuSelectTtl, div.price span"))))
print(item_name_list)
add_price_to_sheet(item_name_list)
