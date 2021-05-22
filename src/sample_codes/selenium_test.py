# chromeをヘッドレスモードで実行するときのオプションのために必要
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import yaml
import time
import random

'''
Chrome Driverの自動更新を実行
'''
# Chrome Driverの最新を自動で更新する（ローカル環境用）
from webdriver_manager.chrome import ChromeDriverManager

# プロキシの設定
PROXY = [
    '160.202.40.20:55655',
    '43.224.8.116:6666',
    '160.19.232.85:3128',
    '115.179.210.50:80',
    '160.19.102.98:8080',
    '153.122.86.46:80',
    '160.202.9.53:8080',
    '43.249.224.172:83',
    '160.19.240.58:8080',
    '43.225.66.184:80'
    ]
# PROXY_AUTH = '{userid}:{password}' # IDとパスワード

# ヘッドレス起動のためのオプションを用意
options = Options()
# options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--allow-running-insecure-content')
options.add_argument(f'--proxy-server=http://{PROXY[random.randint(0, len(PROXY)-1)]}')

# Chrome Driver
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.implicitly_wait(10)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://item.rakuten.co.jp/kakko/c4701938/")

    print(driver.page_source)
    title = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "title")))
    print(f'title name: {title}')


    page_width = driver.execute_script('return document.body.scrollWidth')
    page_height = driver.execute_script('return document.body.scrollHeight')
    driver.set_window_size(page_width, page_height)

    # item_units_input_elm = driver.find_element(By.CSS_SELECTOR, "input[class='rItemUnits']")
    # addd_to_shoppin_cart_button_elm = driver.find_element(By.XPATH, '//*[@id="normal_basket_10006065"]/tbody/tr[5]/td/span[2]/span/span[1]/button/span/span')

    item_units_input_elm = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "rItemUnits")))
    # add_to_shoppin_cart_button_elm = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="cart-button add-cart'))).find_element_by_css_selector('span[class="normal"]').find_element_by_tag_name('span')
    add_to_shoppin_cart_button_elm = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="normal_basket_10006065"]/tbody/tr[5]/td/span[2]/span/span[1]/button/span/span')))

    print("===== done finding item units input & shopping cart button =====")

    print(add_to_shoppin_cart_button_elm.text)
    print(item_units_input_elm.get_attribute("value"))
except Exception as e:
    print(e)
    print('##### スクレイピング中にエラーが起きました #####')
finally:
    driver.quit()
