import requests
from bs4 import BeautifulSoup

url = "https://hungphat-jsc.com/vali-nhua-pc/"

# Thêm User-Agent của một trình duyệt phổ biến (Chrome)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup.prettify()[:5000])
else:
    print(f"Lỗi: {response.status_code}")
