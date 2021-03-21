import urllib.request
import requests
from bs4 import BeautifulSoup

class RakutenBooksScraper:

    def __init__(self, item_url):
        self.target_html_tag = '[id="units"]' # 商品の在庫数が表示されているhtmlタグ
        self.item_url = item_url
        self.item_name_html_tag = 'div[id="productTitle"]'
        # self.req = requests.get(self.item_url)
        self.data = urllib.request.urlopen(self.item_url)
        # self.soup = BeautifulSoup(self.req.content, "html.parser")
        self.soup = BeautifulSoup(self.data, "lxml")


    def is_sold_out(self) -> bool:
        '''
        楽天ブックス用：
        * 商品URLの商品在庫があるかどうかを確認する
        '''

        # itemにhtml要素を読み込み、個数が１以上であれば売切れでないと判断
        item = self.soup.select_one(self.target_html_tag)
        if item == None:
            item_value = 0
            return True # 売り切れ
        else:
            item_value = item['value']
            return False # 在庫あり


    def get_item_name(self) -> str:

        '''
        商品名をページ上から取得してくる
        '''
        item_name_bs4 = self.soup.find(self.item_name_html_tag)

        if item_name_bs4 is not None:
            item_name = item_name_bs4.h1.text
            print(f"item_name: {item_name}")
            return item_name
        else:
            return "NO ITEM NAME"


class RakutenIchibaScraper():

    def __init__(self, item_url):
        self.target_html_tag = "[class='rItemUnits']" # 商品の在庫数が表示されているhtmlタグ
        self.item_url = item_url
        self.item_name_html_tag = "span[class='item_name']"
        self.req = requests.get(self.item_url)
        self.soup = BeautifulSoup(self.req.content, "html.parser")


    def is_sold_out(self) -> bool:
        '''
        楽天市場用：
        * 商品URLの商品在庫があるかどうかを確認する
        '''

        # itemにhtml要素を読み込み、個数が１以上であれば売切れでないと判断
        item = self.soup.select_one(self.target_html_tag)
        if item == None:
            item_value = 0
            return True # 売り切れ
        else:
            item_value = item['value']
            return False # 在庫あり

    def get_item_name(self) -> str:
        '''
        商品名をページ上から取得してくる
        '''
        item_name_bs4 = self.soup.select_one("[class='item_name']")
    
        if item_name_bs4 is not None:
            item_name = item_name_bs4.b.text
            print(f"item_name: {item_name}")
            return item_name
        else:
            return "NO ITEM NAME"
