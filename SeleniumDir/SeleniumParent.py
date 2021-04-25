import time
from selenium.common.exceptions import NoSuchElementException


class SeleniumParent:
    '''
    selenium: 楽天ブックスのスクレイピング
    '''

    def __init__(self, item_url, driver, target_html_xpath):
        self.target_html_xpath = target_html_xpath  # 商品の在庫数が表示されている要素のxpath
        self.item_url = item_url
        # Chrome Driver
        self.driver = driver
        self.driver.get(item_url)
        time.sleep(2)

    def is_sold_out(self) -> bool:
        '''
        楽天ブックス用：
        * 商品URLの商品在庫があるかどうかを確認する
        '''
        # itemにhtml要素を読み込み、個数が１以上であれば売切れでないと判断
        try:
            item = self.driver.find_element_by_xpath(self.target_html_xpath)
            print(item)
        except NoSuchElementException as e:
            print(e)
            item = None

        if item == None:
            item_value = 0
            return True  # 売り切れ
        else:
            item_value = item.get_attribute('value')
            return False  # 在庫あり
