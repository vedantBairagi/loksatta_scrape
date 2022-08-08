from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import time
import zipfile
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('PROXY_USER')
host = os.getenv('PROXY_IP')
port = os.getenv('PROXY_PORT')
password = os.getenv('PROXY_PASS')

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (host, port, user, password)

def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    option = webdriver.ChromeOptions()
    #option.add_argument("--headless")
    chrome_prefs = {}
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    option.experimental_options["prefs"] = chrome_prefs

    s = Service('./chromedriver')
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        option.add_extension(pluginfile)
    if user_agent:
        option.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(service=s, options=option)
    return driver

driver = get_chromedriver(use_proxy=True)

data = pd.read_csv('links.csv')

for index, one in enumerate(list(data.link)):
    driver.get(one)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    h1 = soup.find('h1').text
    h2 = soup.find('h2', attrs={'class': 'wp-block-post-excerpt__excerpt'}).text
    p_tags = soup.find_all('p')
    content = ' '.join([h1] + [h2] + [p.text for p in p_tags])
    
    with open('111903121-Assignment-Dataset.txt', 'a') as f:
        f.write(content)
    with open(f"articles/{index + 1}.txt", 'w') as fp:
        fp.write(content)
    
    