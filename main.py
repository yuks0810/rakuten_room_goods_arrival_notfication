import gspread
import json
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# 認証情報設定
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'expanded-bebop-246202-a2de23a0eef9.json', scope)

# OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

# 共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = '1rgswOPcI7SHKo3KIKokg9-Pv67YcMitZfTXYEH1ClZ4'

ITEM_URL = "https://item.rakuten.co.jp/hankoya-shop/penpen-wood-01/?iasid=07rpp_10095___ev-kkuorxsc-y8jm-1553edc4-61f7-40ed-a8fb-7ba3a10eb3fb"

my_addr = "dorcushopeino1@gmail.com"
my_pass = "rwqmoyiqmrvgvrlp"

# アイテムの個数を取得


def access_to_google_spread():
    # 共有設定したスプレッドシートのシート1を開く
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheet = workbook.worksheet('通知testシート')
    import_value = worksheet.acell('A1').value
    print(import_value)


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
    item_name_html = soup.find(class_='item_name')

    if int(item_value) >= 1 and item_name_html != None:
        return {"bool": True, "item_name": item_name_html.text}
    else:
        return {"bool": False, "item_name": "商品名はありません"}

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
        msg = create_message(my_addr, my_addr, "商品名のお知らせ",
                             item_presence['item_name'])
    if item_presence['bool'] is False:
        msg = create_message(my_addr, my_addr, "売り切れのお知らせ",
                             item_presence['item_name'])

    send_mail(msg)


# ローカル環境テスト実行用
# main(event='a', context='a')

access_to_google_spread()
