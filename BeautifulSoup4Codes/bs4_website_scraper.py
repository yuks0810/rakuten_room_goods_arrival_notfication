import requests
from bs4 import BeautifulSoup

class RakutenBooksScraper:

    def __init__(self, item_url):
        self.target_html_tag = 'input[name="units"]' # 商品の在庫数が表示されているhtmlタグ
        self.item_url = item_url
        self.item_name_html_tag = 'h1'
        self.proxies = {
                        'http' : "socks5h://localhost:1080",
                        'https' : "socks5h://localhost:1080"
                        }


    def is_sold_out(self) -> bool:
        '''
        楽天ブックス用：
        * 商品URLの商品在庫があるかどうかを確認する
        '''

        r = requests.get(self.item_url, proxies=self.proxies)
        soup = BeautifulSoup(r.content, "html.parser")

        # itemにhtml要素を読み込み、個数が１以上であれば売切れでないと判断
        item = soup.select_one(self.target_html_tag)
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
        item_name_bs4 = soup.select_one(self.item_name_html_tag)
        item_name = item_name_bs4.text

        return item_name


class RakutenIchibaScraper():

    def __init__(self, item_url):
        self.target_html_tag = 'select.rItemUnits' # 商品の在庫数が表示されているhtmlタグ
        self.item_url = item_url
        self.item_name_html_tag = 'span.item_name'
        self.proxies = {
                        'http' : "socks5h://localhost:1080",
                        'https' : "socks5h://localhost:1080"
                        }


    def is_sold_out(self) -> bool:
        '''
        楽天市場用：
        * 商品URLの商品在庫があるかどうかを確認する
        '''

        r = requests.get(self.item_url, proxies=self.proxies)
        soup = BeautifulSoup(r.content, "html.parser")

        # itemにhtml要素を読み込み、個数が１以上であれば売切れでないと判断
        item = soup.select_one(self.target_html_tag)
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
        item_name_bs4 = soup.select_one(self.item_name_html_tag)
        item_name = item_name_bs4.text

        return item_name
