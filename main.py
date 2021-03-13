import gspread, json, requests, random, string
import tweepy
from datetime import datetime as dt, timedelta, timezone
import datetime
from bs4 import BeautifulSoup
import settings
import cells_to_arry

# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']

JST = timezone(timedelta(hours=+9), 'JST')

# 認証情報設定
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'expanded-bebop-246202-a2de23a0eef9.json', scope)

# OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

# 共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = '1rgswOPcI7SHKo3KIKokg9-Pv67YcMitZfTXYEH1ClZ4'

def access_to_google_spread():
    '''
    google spread sheetにアクセスする
    '''
    # 共有設定したスプレッドシートのシート1を開く
    workbook = gc.open_by_key(SPREADSHEET_KEY)
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


def get_item_quantity(item_url):
    '''
    商品URLの商品在庫があるかどうかを確認する
    '''

    r = requests.get(item_url)
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

    if int(item_value) >= 1 and item_name_html is not None:
        return {"bool": True, "item_name": item_name_html.text}
    else:
        return {"bool": False, "item_name": "商品名はありません"}

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
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase

    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])

def main(event, context):
    # google spread sheetに接続
    print('==========商品情報取得==========')
    worksheet = access_to_google_spread()
    item_url = worksheet.acell('A2').value
    rakute_room_url = worksheet.acell('B2').value
    print('==========商品情報取得 end==========')
    
    # 商品の一覧の範囲を取得
    item_index = worksheet.range('A2:G10')
    item_index2d = cells_to_arry.cellsto2darray(item_index, 7)

    print('==========twitter情報取得==========')
    API_KEY = worksheet.acell('J5').value
    API_SECRET_KEY = worksheet.acell('J6').value
    ACCESS_TOKEN = worksheet.acell('J7').value
    ACCESS_TOKEN_SECRET = worksheet.acell('J8').value
    print('==========twitter情報取得 end==========')

    for i, item_row in enumerate(item_index2d):
        if item_row[0].value == "" or tweetable(item_row[4].value) is False:
            continue

        item_presence = get_item_quantity(item_row[0].value)
        item_name = item_presence["item_name"]
        rakute_room_url = item_row[1].value
        rakute_room_url2 = item_row[2].value
        tweetable_words_length = item_row[6]

        if item_presence['bool'] is True:
            rand_str = GetRandomStr(2)

            # twitterに投稿する内容
            msg = '{item_name}{rand_str}\r\n急ぎの方こちら↓\r\n{rakute_room_url2}\r\n{rakute_room_url}'.format(item_name=item_name[:50], rakute_room_url=rakute_room_url, rand_str=rand_str, rakute_room_url2=rakute_room_url2)
            
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
                                
        if item_presence['bool'] is False:
            msg = '{item_name} {rakute_room_url}'.format(item_name=item_name, rakute_room_url=rakute_room_url)
            item_row[5].value = "可能"

    # 二次元になっているリストを１次元に直す
    # 二次元だと書き込めない
    item_index1d = cells_to_arry.cellsto1darray(item_index2d)
    
    # スプレッドシートを更新
    worksheet.update_cells(item_index1d)

# ローカル環境テスト実行用
# main(event='a', context='a')
