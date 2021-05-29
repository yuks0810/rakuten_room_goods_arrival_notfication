import time
import requests
from bs4 import BeautifulSoup


class BeautifulSoupScrayping:
    '''
    '''

    def __init__(self, URL, target_css_selector):        
        self.target_css_selector = target_css_selector

        headers = {"User-Agent": "hoge"}
        resp = requests.get(URL, timeout=20, headers=headers)
        r_text = resp.text
        self.b_soup = BeautifulSoup(r_text, 'html.parser')

        
    def is_sold_out(self) -> bool:
        '''
        楽天ブックス用：
        * 商品URLの商品在庫があるかどうかを確認する
        '''
        
        res = self.__get_requested_elemnt(self.target_css_selector)

        if res["elm"] == None:
            # 売り切れ
            print('売り切れ')
            return True
        else:
            print(f'{res["title"]} => 在庫あり')
            # 在庫あり
            return False


    def __get_requested_elemnt(self, target_css_selector):
        page_title = self.b_soup.find('title')
        elm = self.b_soup.select_one(target_css_selector)
        print(elm)

        return dict(elm=elm, title=page_title)
