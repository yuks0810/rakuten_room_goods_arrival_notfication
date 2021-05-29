import requests
from bs4 import BeautifulSoup
 
URL = 'https://item.rakuten.co.jp/kakko/c4701938/'
headers = {"User-Agent": "hoge"}

resp = requests.get(URL, timeout=1, headers=headers)
r_text = resp.text

b_soup = BeautifulSoup(r_text, 'html.parser')
elm =b_soup.select_one("input[class='rItemUnits']")
# elm =b_soup.select_one('input[class="rItemUnits"]')
print(elm)

if elm:
    print("yes")
