import requests
from bs4 import BeautifulSoup
 
URL = "https://www.cman.jp/network/support/go_access.cgi"
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
 
proxies = {
    'http':'https://140.227.237.154:1000',
    'https':'https://140.227.237.154:1000'
}
 
# User-Agentの設定
headers = {"User-Agent": USER_AGENT}
 
resp = requests.get(URL, proxies=proxies, headers=headers, timeout=30)
resp.encoding = 'utf8' 
soup = BeautifulSoup(resp.text, "html.parser")
 
# IP表示部分の取得
ip = soup.find(class_="outIp").text
 
print(ip)
