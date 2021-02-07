import time
import datetime
import sys
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

ITEM_URL = "https://item.rakuten.co.jp/finebookpremiere/10003220/?gclid=Cj0KCQiAmfmABhCHARIsACwPRADAlAREiKuQHirblXntpVMoxCAL7Nj993L8Z1DyzqfZYVZezcB5LBYaAir4EALw_wcB&scid=af_pc_etc&sc2id=af_113_0_10001868&icm_acid=288-622-7470&icm_agid=58708966751&icm_cid=1424232125&gclid=Cj0KCQiAmfmABhCHARIsACwPRADAlAREiKuQHirblXntpVMoxCAL7Nj993L8Z1DyzqfZYVZezcB5LBYaAir4EALw_wcB_"

my_addr = "dorcushopeino1@gmail.com"
my_pass = "rwqmoyiqmrvgvrlp"

# アイテムの個数を取得
def get_item_quantity():
    r = requests.get(ITEM_URL)
    soup = BeautifulSoup(r.content, "html.parser")

    # itemにhtml要素を読み込み、個数が１以上であれば売切れでないと判断
    item = soup.find('input', class_='rItemUnits')
    if item == None:
        item_value = 0
    else:
        item_value = item['value']

    """
    商品が売切れでない時は
    bool = True
    としてitem_nameを返す

    売り切れの場合は
    bool = False
    としてitem_nameを返す
    """
    # item_name = soup.find(class_='item_name').text
    item_name = "test texttexttexttexttexttexttexttexttexttexttext"
    if int(item_value) >= 1:
        return {"bool": True, "item_name": item_name}
    else:
        return {"bool": False, "item_name": item_name}

# メッセージの作成
def create_message(from_addr, to_addr, subject, body_txt):
    msg = MIMEText(body_txt)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    return msg

# メールの送信
def send_mail(msg):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(my_addr, my_pass)
        server.send_message(msg)

def main(event, context):
    item_presence = get_item_quantity()
    if item_presence['bool'] is True:
        msg = create_message(my_addr, my_addr, "商品名のお知らせ", item_presence['item_name'])
    if item_presence['bool'] is False:
        msg = create_message(my_addr, my_addr, "売り切れのお知らせ", item_presence['item_name'])

    send_mail(msg)

# ローカル環境テスト実行用
# main(event='a', context='a')