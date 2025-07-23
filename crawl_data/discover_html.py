import requests
from bs4 import BeautifulSoup

# Test với 1 URL cụ thể
url = "https://hungphat-jsc.com.vn/vali-nhua-hung-phat-2103"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Inspect actual HTML structure
print(soup.prettify()[:5000])