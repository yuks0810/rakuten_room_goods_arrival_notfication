import gspread, json, random, string
import tweepy
from datetime import datetime as dt, timedelta, timezone
import datetime
import settings # dotenv
import cells_to_arry

# スクレイピング
from SeleniumDir.SeleniumParent import SeleniumParent

# Chrome Driverのために必要
import chromedriver_binary
from selenium.webdriver.chrome.options import Options # chromeをヘッドレスモードで実行するときのオプションのために必要
from selenium import webdriver

# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

import yaml
with open('config.yml', 'r') as yml:
    config = yaml.safe_load(yml)

scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']

JST = timezone(timedelta(hours=+9), 'JST')

# 認証情報設定
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'expanded-bebop-246202-a2de23a0eef9.json', scope)

# OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)


def auto_renew_chrome_driver():
    '''
    Chrome Driverの自動更新を実行
    '''
    # Chrome Driverの最新を自動で更新する（ローカル環境用）
    from webdriver_manager.chrome import ChromeDriverManager

    # ヘッドレス起動のためのオプションを用意
    option = Options()                          
    option.add_argument('--headless')   

    # Chrome Driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
    return driver


def set_up_chrome_driver():
    '''
    Lambdaで動作するようにChrome Driver設定
    '''
    options = webdriver.ChromeOptions()
    options.binary_location = "./bin/headless-chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(executable_path="./bin/chromedriver", chrome_options=options)
    return driver


def access_to_google_spread():
    '''
    google spread sheetにアクセスする
    '''
    # 共有設定したスプレッドシートのシート1を開く
    workbook = gc.open_by_key(config['spreadsheet_key'])
    worksheet = workbook.worksheet('通知testシート')

    return worksheet


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
    datetime_last_tweet_date = datetime.datetime(year=last_tweet_date.year, month=last_tweet_date.month, day=last_tweet_date.day, hour=last_tweet_date.hour, minute=last_tweet_date.minute, second=last_tweet_date.second)

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
    
    if test_mode:
        # ローカル環境用
        driver = auto_renew_chrome_driver()
    else:
        # lambda環境用
        driver = set_up_chrome_driver()

    # google spread sheetに接続
    print('==========spread sheet接続 start==========')
    worksheet = access_to_google_spread()
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
    API_KEY = worksheet.acell('J5').value
    API_SECRET_KEY = worksheet.acell('J6').value
    ACCESS_TOKEN = worksheet.acell('J7').value
    ACCESS_TOKEN_SECRET = worksheet.acell('J8').value
    print('==========twitter情報取得 end==========')

    for i, item_row in enumerate(item_index2d):
        if item_row[0].value == "" or tweetable(item_row[4].value) is False:
            continue
        
        item_url = item_row[0].value
        rakute_room_url = item_row[1].value
        rakuten_affiliate_url = item_row[2].value
        
        if "books.rakuten.co.jp" in item_url:
            # 楽天ブックスの場合
            print('=====楽天ブックススクレイピング start=====')
            rakute_bools_scraper = SeleniumParent(
                item_url=item_url,
                driver=driver,
                target_html_xpath=config["rakuten_books"]["target_xpath"]
                )
            sold_out = rakute_bools_scraper.is_sold_out()
            print('=====楽天ブックススクレイピング end=====')
        elif "item.rakuten.co.jp" in item_url:
            # 楽天市場の場合
            print('=====楽天市場スクレイピング start=====')
            rakute_ichiba_scraper = SeleniumParent(
                item_url=item_url,
                driver=driver,
                target_html_xpath=config["rakuten_ichiba"]["target_xpath"]
                )
            sold_out = rakute_ichiba_scraper.is_sold_out()
            print('=====楽天市場スクレイピング end=====')
        else:
            continue

        if sold_out is False:
            print("=====在庫あり=====")
            rand_str = GetRandomStr(2)

            # twitterに投稿する内容を作成
            msg = '{rand_str}\r\n急ぎの方こちら↓\r\n{rakuten_affiliate_url}\r\n{rakute_room_url}'.format(
                rakute_room_url=rakute_room_url,
                rand_str=rand_str,
                rakuten_affiliate_url=rakuten_affiliate_url
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

    return {
        'status_code': 200
        }

if __name__ == '__main__':
    # ローカル環境で実行するときはtest_mode=Trueにする
    print(lambda_handler(event=None, context=None, test_mode=True))
