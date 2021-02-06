import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

kawase_url = "https://www.nikkei.com/markets/kawase/"

my_addr = "dorcushopeino1@gmail.com"
my_pass = "rwqmoyiqmrvgvrlp"

# 為替の取得
def get_kawase_price():
    r = requests.get(kawase_url)
    soup = BeautifulSoup(r.content, "html.parser")
    price_elems = soup.select("div.mkc-stock_prices")
    return price_elems[0].getText()

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
    price = get_kawase_price()
    if price:
        msg = create_message(my_addr, my_addr, "ドル円レートお知らせ", price)
        send_mail(msg)

# import time
# import datetime
# import sys
# # import classes
# from browser_controll import BrowserControll
# # selenium chrome driverの最新verをインストール
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options # オプションを使うために必要

# # g_spread
# from g_spread_sheet.box_score_g_spread import BoxScoreGSpread
# from g_spread_sheet.game_report_g_spread import GameReportGSpread
# from g_spread_sheet.play_by_play_g_spread import PlayByPLayGSpread

# """
# 常に最新のchrome driverを使えるようにスクリプトを回す毎にインストールする
# """
# print('updating chrome driver start')
# option = Options()                          # オプションを用意
# option.add_argument('--headless')           # ヘッドレスモードの設定を付与

# # ヘッドレスで実行するとき
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)

# # ブラウザを表示するとき
# # driver = webdriver.Chrome(ChromeDriverManager().install())
# print('updating chrome driver end')


# # Webページへアクセス
# driver.get('https://www.bleague.jp/schedule/?s=1&tab={tab}&year={season}&event={event}&club=&setuFrom={setuFrom}'.format(tab=league, year=league, event=event, setuFrom=setuFrom, season=season.split('-')[0]))
# driver.implicitly_wait(15)