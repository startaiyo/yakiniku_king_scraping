import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from flask import Blueprint, jsonify, request, render_template

api = Blueprint('main', __name__, url_prefix = '/yakiniku_king')

# use creds to create a client to interact with the Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('app/apis/client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
book = client.open("焼肉キング戦いの記録")
sheet = book.worksheet('2022/12/3')

# Extract and print all of the values
# list_of_hashes = sheet.get_all_values()

data = [['北海道夢の大地豚壺漬け豚ジンギスカン', 690, 759, '期間限定'], ['旭川発祥一本塩ホルモン※数量限定', 390, 429, '期間限定'], ['紅ずわいのコールスロー※数量限定', 390, 429, '期間限定']]

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
    item_list = [["品名", "本体価格", "税込み価格", "ジャンル"]] + item_list
    price_sheet.append_rows(item_list)

def add_record_to_new_sheet(record_list):
    DIFF_JST_FROM_UTC = 9
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
    now_for_title = now.strftime('%Y/%m/%d')
    exist_worksheets = list(map(lambda x: x.title, book.worksheets()))
    if exist_worksheets.index(now_for_title) > 0:
        new_worksheet = book.worksheet(now_for_title)
    else:
        new_worksheet = book.add_worksheet(now_for_title, rows = 100, cols = 4)
    filtered_record_list = list(filter(lambda x: x[4] != '0', record_list))
    print(filtered_record_list)
    new_worksheet.append_rows(filtered_record_list)


def make_num(price_info):
    price_info[1] = int(price_info[1].replace("円", "").replace(",", ""))
    price_info[2] = int(price_info[2].replace("円)", "").replace("(税込", "").replace(",", ""))
    return price_info

@api.route('')
def render_page():
    return render_template('index.html')

@api.route('/api/register', methods = ['GET', 'POST'])
def show_menu():
    if request.method == 'POST':
        result_sets = []
        for key, value in request.form.items():
            if value != "":
                result_sets.append(key.split(",") + [value])
        add_record_to_new_sheet(result_sets)
    menu_sheet = book.worksheet('値段リスト')
    menu_list = menu_sheet.get_all_values()[1:]
    return render_template('index.html', data = menu_list)

@api.route('/api/renew')
def renew_all():
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
        menu_title = soup.select("h1.pageTitle")[0].text
        # [menu, price, tax-in price]
        item_and_price_list = list(split_list(list(map(lambda x: "".join(x.text.split()), soup.select("div.item_description h2, div.item_description span"))),3))
        # [menu, price, tax-in price, title]
        item_and_menu_title_and_price_list = list(map(lambda x: x + [menu_title], item_and_price_list))
        item_name_list.extend(item_and_menu_title_and_price_list)
    response_for_kikan_gentei = requests.get("https://www.yakiniku-king.jp/menu_all/season/")
    all_kikan_gentei = BeautifulSoup(response_for_kikan_gentei.content, 'html.parser').select('a[href*="menu_all/season"]')
    all_href_list_kikan_gentei = list(set(list(map(lambda x: "https://www.yakiniku-king.jp" + x.get('href'), all_kikan_gentei))))
    kikan_gentei_tag_href_list = list(filter(lambda x: not x.replace("/","").endswith("season"), all_href_list_kikan_gentei))
    for url in kikan_gentei_tag_href_list:
        time.sleep(0.5)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        item_name_list.append(list(map(lambda x: "".join(x.text.split()), soup.select("div.menuSelectTtl, div.price span"))) + ["期間限定"])
    item_name_list_using_num = list(map(make_num, item_name_list))
    add_price_to_sheet(item_name_list_using_num)
    return jsonify({"text": "最新の状態です！！"}), 200