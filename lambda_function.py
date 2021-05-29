import argparse
import gspread
import random
import string
import tweepy
from datetime import datetime as dt, timedelta, timezone
import datetime
# import settings  # dotenv
from src.GspreadControll import cells_to_arry
from src.BeautifulSoup.beautifulSoupPareint import BeautifulSoupScrayping


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


def tweetable(last_tweet_date):
    '''
    30分以内にtweetしたかどうかを判断する
    '''
    if not last_tweet_date:
        return True
    last_tweet_date = dt.strptime(last_tweet_date, '%Y/%m/%d %H:%M:%S')
    datetime_now = get_current_date()
    datetime_last_tweet_date = datetime.datetime(
        year=last_tweet_date.year,
        month=last_tweet_date.month,
        day=last_tweet_date.day,
        hour=last_tweet_date.hour,
        minute=last_tweet_date.minute,
        second=last_tweet_date.second
    )

    # スプレッドシートに記載されている時間と、JSTの現在時刻を比較
    timegap = datetime_now - datetime_last_tweet_date
    # 30分以上の差があればTrueとする
    if timegap.seconds > 1800:
        return True
    else:
        return False


def GetRandomStr(num):
    '''
    twitterで同じ文章を連投できないのでランダムな２文字の文字列を
    文章の末尾に追加してエラーを回避するためのもの
    '''
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])


def lambda_handler(event, context, test_mode=False):
    '''
    メイン関数
    event, contextは "AWS Lambda" で動かすのに必要な引数
    '''
    print('event: {}'.format(event))
    print('context: {}'.format(context))


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

    for i, item_row in enumerate(item_index2d):
        if item_row[0].value == "" or tweetable(item_row[4].value) is False:
            continue

        item_url = item_row[0].value
        rakute_room_url = item_row[1].value
        rakuten_affiliate_url = item_row[2].value
        post_message = item_row[3].value

        if "books.rakuten.co.jp" in item_url:
            # 楽天ブックスの場合
            print('=====楽天ブックススクレイピング start=====')
            rakute_books_scraper = BeautifulSoupScrayping(
                URL=item_url,
                target_css_selector="button[class='new_addToCart_kobo']"
            )
            sold_out = rakute_books_scraper.is_sold_out()
            print(sold_out)
            print('=====楽天ブックススクレイピング end=====')
        elif "item.rakuten.co.jp" in item_url:
            # 楽天市場の場合
            print('=====楽天市場スクレイピング start=====')
            rakute_ichiba_scraper = BeautifulSoupScrayping(
                URL=item_url,
                target_css_selector="input[class='rItemUnits']"
            )
            sold_out = rakute_ichiba_scraper.is_sold_out()
            print('=====楽天市場スクレイピング end=====')
        else:
            continue

        if sold_out is False:
            print("=====在庫あり=====")
            rand_str = GetRandomStr(2)

            # twitterに投稿する内容を作成
            msg = '{rand_str}\r\n{post_message}\r\n{rakuten_affiliate_url}\r\n{rakute_room_url}'.format(
                rakute_room_url=rakute_room_url,
                rand_str=rand_str,
                rakuten_affiliate_url=rakuten_affiliate_url,
                post_message=post_message
            )

            print(f"tweet可能？：{tweetable(item_row[4].value)}")
            if tweetable(item_row[4].value):
                tdatetime = get_current_date()
                tstr = tdatetime.strftime('%Y/%m/%d %H:%M:%S')
                item_row[4].value = tstr
                item_row[5].value = "不可"

                # ツイート
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
    return {'status_code': 200}


if __name__ == '__main__':
    # 引数を設定
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_mode', action='store_true')
    args = parser.parse_args()

    # ローカル環境で実行するときはtest_mode=Trueにする
    print(lambda_handler(event=None, context=None, test_mode=args.test_mode))
