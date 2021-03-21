import time



class SeleniumRakutenBooksScraper:
    '''
    selenium: 楽天ブックスのスクレイピング
    '''

    def __init__(self, item_url, driver):
        self.target_html_tag = '[id="units"]' # 商品の在庫数が表示されているhtmlタグ
        self.item_name_html_tag = '//*[@id="productTitle"]/h1'

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
            # 要素がある場合の処理
            item = self.driver.find_element_by_css_selector(self.target_html_tag)
            if item == None:
                item_value = 0
                return True # 売り切れ
            else:
                item_value = item.get_attribute('value')
                return False # 在庫あり
        except:
            print('個数表示inputを取得できませんでした。')


    def get_item_name(self) -> str:
        '''
        商品名をページ上から取得してくる
        '''
        try:
            # 要素がある場合の処理
            item_name_bs4 = self.driver.find_element_by_xpath(self.item_name_html_tag)

            if item_name_bs4 is not None:
                item_name = item_name_bs4.text
                print(f"item_name: {item_name}")
                return item_name
            else:
                return "NO ITEM NAME"
        except:
            # 要素がない場合の処理（※正確にはtryの内容を実行してエラーが起こる場合の処理）
            print("ページを名取得できませんでした。")
            

class SeleniumIchibaScraper:
    '''
    selenium: 楽天市場のスクレイピング
    '''

    def __init__(self, item_url, driver):
        # 商品の在庫数が表示されているxpath
        self.target_html_tag = '//*[@id="units"]'
        
        # 商品名が表示されているxpath
        self.item_name_html_tag = '//*[@id="pagebody"]/table[2]/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td[3]/table[2]/tbody/tr/td/table[5]/tbody/tr/td[3]/table[1]/tbody/tr[1]/td/span[2]/b'

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
            # 要素がある場合の処理
            item = self.driver.find_element_by_xpath(self.target_html_tag)
            if item == None:
                item_value = 0
                return True # 売り切れ
            else:
                item_value = item.get_attribute('value')
                return False # 在庫あり
        except:
            # 要素がない場合の処理（※正確にはtryの内容を実行してエラーが起こる場合の処理）
            print('個数のinput要素を取得できませんでした。')


    def get_item_name(self) -> str:
        '''
        商品名をページ上から取得してくる
        '''

        try:
            # 要素がある場合の処理
            item_name_bs4 = self.driver.find_element_by_xpath(self.item_name_html_tag)
        
            if item_name_bs4 is not None:
                item_name = item_name_bs4.text
                print(f"item_name: {item_name}")
                return item_name
            else:
                return "NO ITEM NAME"
        except:
            # 要素がない場合の処理（※正確にはtryの内容を実行してエラーが起こる場合の処理）
            print('商品名を取得できませんでした。')
