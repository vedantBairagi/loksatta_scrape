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
base_url = "https://www.loksatta.com/latest-news/page/"
# Each page contains at least 20 articles so I will need to scrape at least 250 pages to get 5000
# instances



fname = 'links.csv'
link_d = {'time': [], 'link':[]}
t_links = []




for pno in range(1, 301):
    p_url = f"{base_url}{pno}"
    driver.get(p_url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    articles = soup.find_all('article')

    for a in articles:
        link = a.find_all('a')[0]['href']
        link_d['link'].append(link)
        link_d['time'].append(datetime.now())
    #driver.close()

pd.DataFrame(link_d).to_csv(fname)

        

