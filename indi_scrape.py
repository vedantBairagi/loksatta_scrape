import requests
import pandas as pd
from requests.auth import HTTPProxyAuth
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

import urllib3
from urllib3 import make_headers, ProxyManager
default_headers = make_headers(proxy_basic_auth='111903121:DGZ36')
http = ProxyManager("https://10.1.101.150:3128", proxy_headers=default_headers)


data = pd.read_csv('links.csv')
proxies = {'https': 'https://111903121:DGZ36@10.1.101.150:3128'}

for index, one in enumerate(list(data.link)[:5]):
    one_get = http.request('GET', one).data.decode('utf-8')
    soup = BeautifulSoup(one_get, 'lxml')
    h1 = soup.find('h1').text
    h2 = soup.find('h2', attrs={'class': 'wp-block-post-excerpt__excerpt'}).text
    p_tags = soup.find_all('p')
    content = ' '.join([h1] + [h2] + [p.text for p in p_tags])
    '''
    with open('111903121-Assignment-Dataset.txt', 'a') as f:
        f.write(content)
    with open(f"articles/{index + 1}.txt", 'w') as fp:
        fp.write(content)
    '''
    with open(f'{index}auth_success.txt', 'w') as ap:
        ap.write(content)
