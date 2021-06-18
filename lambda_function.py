import argparse
from os import curdir
import gspread
import random
import string
import tweepy
from datetime import datetime as dt, timedelta, timezone
import datetime
# import settings  # dotenv
from src.GspreadControll import cells_to_arry
from src.BeautifulSoup.beautifulSoupPareint import BeautifulSoupScrayping

from mysql.query import (
    create_db_connection,
    close_db_connections,
    insert_into_products_table,
    update_set_products_table,
    select_from_products_table
)


# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

import yaml
with open('src/SeleniumDir/config.yml', 'r') as yml:
    config = yaml.safe_load(yml)

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

JST = timezone(timedelta(hours=+9), 'JST')

# 認証情報設定
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'src/expanded-bebop-246202-a2de23a0eef9.json', scope)

# OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)


def access_to_google_spread():
    '''
    google spread sheetにアクセスする
    '''
    # 共有設定したスプレッドシートのシート1を開く
    workbook = gc.open_by_key(config['spreadsheet_key'])
    worksheet = workbook.worksheet('通知testシート')
    api_key_worksheet = workbook.worksheet('API_KEYS')

    return worksheet, api_key_worksheet


def get_current_date():
    # 日本時間で現在時間を取得する
    timenow = dt.now(JST)
    current_time_in_datetime = datetime.datetime(
        year=timenow.year,
        month=timenow.month,
        day=timenow.day,
        hour=timenow.hour,
        minute=timenow.minute,
        second=timenow.second
    )

    return current_time_in_datetime


def tweetable(rakuten_product_url):
    '''
    30分以内にtweetしたかどうかを判断する。
    rakute_urlでDBを検索して、
    最後に通知した値を取得する

    return:
        - True -> ツイート可能
        - False -> ツイート不可
    '''
    # 空白を削除
    rakuten_product_url = rakuten_product_url.strip()
    # DBから該当の楽天URLを持つデータを取得する
    row = select_from_products_table(rakuten_product_url)
    print(row)
    # 現在時刻を取得
    datetime_now = get_current_date()

    if row == None:
        # データがない場合は新規にデータを作成
        insert_into_products_table(rakuten_product_url=rakuten_product_url, latest_notification_date=datetime_now)
        return True
    else:
        id = row[0]
        latest_tweet_date = row[1]
        timegap = datetime_now - latest_tweet_date
        if timegap.seconds > 1800:
            # 最後の通知から30分経過していたら、最終通知時間をUpdateして Trueを返す（Tweet可能）dddd
            return True
        else:
            # 30分経過していなかったら、Falseを返す。（Tweetできない）
            return False


def lambda_handler(event, context, test_mode=False):
    '''
    メイン関数
    event, contextは "AWS Lambda" で動かすのに必要な引数
    '''
    print('event: {}'.format(event))
    print('context: {}'.format(context))

    # DBに接続
    global conn, cur
    conn, cur = create_db_connection()

    # google spread sheetに接続
    print('==========spread sheet接続 start==========')
    worksheet, api_key_worksheet = access_to_google_spread()
    # 商品の一覧の範囲を取得
    item_index = worksheet.range('A2:G10')
    # ２次元配列にした方が操作しやすいため、item_indexを２次元配列に変換
    item_index2d = cells_to_arry.cellsto2darray(item_index, 7)
    print('==========spread sheet接続 end==========')

    # テスト用（.envから読み取っている）
    # API_KEY = settings.API_KEY
    # AIP_KEY_SECRET = settings.API_KEY_SECRET
    # ACCESS_TOKEN = settings.ACCESS_TOKEN
    # ACCESS_TOKEN_SECRET = settings.ACCESS_TOKEN_SECRET

    print('==========twitter情報取得==========')
    API_KEY = str(api_key_worksheet.acell('B1').value.strip())
    API_SECRET_KEY = str(api_key_worksheet.acell('B2').value.strip())
    ACCESS_TOKEN = str(api_key_worksheet.acell('B3').value.strip())
    ACCESS_TOKEN_SECRET = str(api_key_worksheet.acell('B4').value.strip())
    print('==========twitter情報取得 end==========')

    for item_row in item_index2d:
        if item_row[0].value == "" or tweetable(item_row[0].value) is False:
            continue

        rakuten_product_url = str(item_row[0].value).strip()
        rakute_room_url = str(item_row[1].value).strip()
        rakuten_affiliate_url = str(item_row[2].value).strip()
        post_message = item_row[3].value

        if "books.rakuten.co.jp" in rakuten_product_url:
            # 楽天ブックスの場合
            print('=====楽天ブックススクレイピング start=====')
            rakute_books_scraper = BeautifulSoupScrayping(
                URL=rakuten_product_url,
                target_css_selector="input[id='units']"
            )
            sold_out = rakute_books_scraper.is_sold_out()
            print(sold_out)
            print('=====楽天ブックススクレイピング end=====')

        if "item.rakuten.co.jp" in rakuten_product_url:
            # 楽天市場の場合
            print('=====楽天市場スクレイピング start=====')
            rakute_ichiba_scraper = BeautifulSoupScrayping(
                URL=rakuten_product_url,
                target_css_selector="input[class='rItemUnits']"
            )
            sold_out = rakute_ichiba_scraper.is_sold_out()
            print('=====楽天市場スクレイピング end=====')

        if sold_out is False:
            print("=====在庫あり=====")

            # twitterに投稿する内容を作成
            msg = f'{get_current_date()}\r\n{post_message}\r\n{rakuten_affiliate_url}\r\n{rakute_room_url}'

            print(f"tweet可能？：{tweetable(item_row[0].value)}")
            if tweetable(item_row[0].value):
                tdatetime = get_current_date()
                tstr = tdatetime.strftime('%Y/%m/%d %H:%M:%S')
                item_row[4].value = tstr
                item_row[5].value = "不可"

                # DBをアップデート
                update_set_products_table(rakuten_product_url, latest_notification_date=tdatetime)

                # ツイート実行
                auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
                auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                api = tweepy.API(auth)
                api.update_status(msg)
                print('=====SpreadSheetに書き込みを行いました=====')

        if sold_out is True:
            msg = '{rakute_room_url}'.format(
                rakute_room_url=rakute_room_url
            )
            item_row[5].value = "可能"

    # 二次元になっているリストを１次元に直す
    # 二次元だと書き込めない
    item_index1d = cells_to_arry.cellsto1darray(item_index2d)

    # スプレッドシートを更新
    worksheet.update_cells(item_index1d)

    # DBセッションを閉じる
    close_db_connections()

    return {'status_code': 200}


if __name__ == '__main__':
    # 引数を設定
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_mode', action='store_true')
    args = parser.parse_args()

    # ローカル環境で実行するときはtest_mode=Trueにする
    print(lambda_handler(event=None, context=None, test_mode=args.test_mode))
