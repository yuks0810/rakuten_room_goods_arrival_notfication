import sys

# main.pyをimportするのに上位階層に移動する必要がある
from pathlib import Path
sys.path.append(str(Path('__file__').resolve().parent))

import main

def test_auto_renew_chrome_driver():
    '''
    seleniumのdriverのテスト
    '''
    driver_type = "<class 'selenium.webdriver.chrome.webdriver.WebDriver'>"
    driver = str( type(main.auto_renew_chrome_driver()))
    assert driver == driver_type


def test_access_to_google_spread():
    '''
    google spread sheetにアクセスするコードのテスト
    '''
    worksheet_type = "<class 'gspread.models.Worksheet'>"
    worksheet = str(type(main.access_to_google_spread()))
    assert worksheet == worksheet_type


def test_get_current_date():
    '''
    現在時刻を日本時間で取得できるかテスト
    '''


def test_tweetable():
    '''
    tweet可能状況をテスト
    '''
