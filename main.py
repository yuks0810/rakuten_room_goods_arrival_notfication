import time
import argparse
from os import curdir
import gspread
import tweepy
from datetime import datetime as dt, timedelta, timezone
import pytz
import datetime
# import settings  # dotenv
from src.GspreadControll import cells_to_arry
from src.BeautifulSoup.beautifulSoupPareint import BeautifulSoupScrayping
from logs import logger

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

logger = logger.setup_logger(__name__, logfile="./logs/access.log")

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


def get_current_date():
    # 日本時間で現在時間を取得する
    JST = timezone(timedelta(hours=+9), 'JST')
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


class ScraypingProcessor:
    def __init__(self):
        # DBに接続
        global conn, cur
        conn, cur = create_db_connection()


    def __del__(self):
        # インスタンスを削除するときにDBセッションを閉じる
        close_db_connections()


    def access_to_google_spread(self):
        '''
        google spread sheetにアクセスする
        '''
        # 共有設定したスプレッドシートのシート1を開く
        workbook = gc.open_by_key(config['spreadsheet_key'])
        worksheet = workbook.worksheet('通知testシート')
        api_key_worksheet = workbook.worksheet('API_KEYS')

        return worksheet, api_key_worksheet


    def tweetable(self, rakuten_product_url):
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
        logger.info(row)
        # 現在時刻を取得
        datetime_now = get_current_date()

        if row == None:
            # データがない場合は新規にデータを作成
            insert_into_products_table(
                rakuten_product_url=rakuten_product_url, latest_notification_date=datetime_now)
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


    def connect_to_google_spread_sheet(self):
        # google spread sheetに接続
        logger.info('==========spread sheet接続 start==========')
        worksheet, api_key_worksheet = self.access_to_google_spread()
        # 商品の一覧の範囲を取得
        item_index = worksheet.range('A2:G10')
        # ２次元配列にした方が操作しやすいため、item_indexを２次元配列に変換
        item_index2d = cells_to_arry.cellsto2darray(item_index, 7)
        logger.info('==========spread sheet接続 end==========')

        return worksheet, api_key_worksheet, item_index2d


    def get_twitter_account_keys(self, api_key_worksheet):
        logger.info('==========twitter情報取得==========')
        API_KEY = str(api_key_worksheet.acell('B1').value.strip())
        API_SECRET_KEY = str(api_key_worksheet.acell('B2').value.strip())
        ACCESS_TOKEN = str(api_key_worksheet.acell('B3').value.strip())
        ACCESS_TOKEN_SECRET = str(api_key_worksheet.acell('B4').value.strip())
        logger.info('==========twitter情報取得 end==========')

        return API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


    def scrayping_process(self, rakuten_product_url, rakute_room_url, rakuten_affiliate_url, post_message, item_row):
        """
        対処のURLのスクレイピングを行い、Twitter投稿するまでの処理
        """
        if "books.rakuten.co.jp" in rakuten_product_url:
            # 楽天ブックスの場合
            logger.info('=====楽天ブックススクレイピング start=====')
            rakute_books_scraper = BeautifulSoupScrayping(
                URL=rakuten_product_url,
                target_css_selector="input[id='units']"
            )
            sold_out = rakute_books_scraper.is_sold_out()
            logger.info(sold_out)
            logger.info('=====楽天ブックススクレイピング end=====')

        if "item.rakuten.co.jp" in rakuten_product_url:
            # 楽天市場の場合
            logger.info('=====楽天市場スクレイピング start=====')
            rakute_ichiba_scraper = BeautifulSoupScrayping(
                URL=rakuten_product_url,
                target_css_selector="input[class='rItemUnits']"
            )
            sold_out = rakute_ichiba_scraper.is_sold_out()
            logger.info('=====楽天市場スクレイピング end=====')

            if sold_out is False:
                # 在庫がある時の処理
                # スプレッドシートへの書き込みと、twitterへのツイートを行う
                logger.info("=====在庫あり=====")

                # twitterに投稿する内容を作成
                msg = f'{get_current_date()}\r\n{post_message}\r\n{rakuten_affiliate_url}\r\n{rakute_room_url}'

                logger.info(f"tweet可能？：{self.tweetable(item_row[0].value)}")
                if self.tweetable(item_row[0].value):
                    tdatetime = get_current_date()
                    tstr = tdatetime.strftime('%Y/%m/%d %H:%M:%S')
                    item_row[4].value = tstr
                    item_row[5].value = "不可"

                    # DBをアップデート
                    update_set_products_table(
                        rakuten_product_url, latest_notification_date=tdatetime)

                    # ツイート実行
                    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
                    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                    api = tweepy.API(auth)
                    api.update_status(msg)
                    logger.info('=====SpreadSheetに書き込みを行いました=====')

            if sold_out is True:
                # 売り切れの時の処理
                msg = '{rakute_room_url}'.format(
                    rakute_room_url=rakute_room_url
                )
                item_row[5].value = "可能"


    def main(self):
        '''
        メイン関数
        '''
        # Google Spread Sheetに接続
        worksheet, api_key_worksheet, item_index2d = self.connect_to_google_spread_sheet()

        # スプレッドシートからtwiterの認証鍵類を取得
        global API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET = self.get_twitter_account_keys(api_key_worksheet)

        for item_row in item_index2d:
            if item_row[0].value == "" or self.tweetable(item_row[0].value) is False:
                continue
            else:
                # スクレイピング可能状態である時の処理
                # 必要な情報をスプレッドシートから取得
                rakuten_product_url = str(item_row[0].value).strip()
                rakute_room_url = str(item_row[1].value).strip()
                rakuten_affiliate_url = str(item_row[2].value).strip()
                post_message = item_row[3].value

                # スクレイピング処理
                self.scrayping_process(
                    rakuten_product_url,
                    rakute_room_url,
                    rakuten_affiliate_url,
                    post_message,
                    item_row
                )

        # 二次元になっているリストを１次元に直す
        # 二次元だと書き込めない
        item_index1d = cells_to_arry.cellsto1darray(item_index2d)

        # スプレッドシートを更新
        worksheet.update_cells(item_index1d)

        return {'status_code': 200}


if __name__ == '__main__':
    timenow = get_current_date() + datetime.timedelta(days=-4, hours=19, minutes=50)
    # timenow = get_current_date()
    am_6 = datetime.datetime(
        year=timenow.year,
        month=timenow.month,
        day=timenow.day,
        hour=6,
        minute=0,
        second=0
    )

    am_24 = datetime.datetime(
        year=timenow.year,
        month=timenow.month,
        day=timenow.day+1,
        hour=0,
        minute=0,
        second=0
    )

    print(am_6)
    print(am_24)
    print(timenow)

    # ローカル環境で実行するときはtest_mode=Trueにする
    # while am_6 <= timenow <= am_24:
    #     time.sleep(1)
    #     print("sleep 1 sec")
    #     scraping_processor = ScraypingProcessor()
    #     scraping_processor.main()
    #     del scraping_processor
