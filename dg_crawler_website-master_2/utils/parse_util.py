import random
import requests
import json
import re
from common.header import UA_LIST
from bs4 import BeautifulSoup
from lxml import etree
from scrapy.selector import SelectorList
ua = {
    'user-agent': random.choice(UA_LIST)
}


def GET(url: str, headers=None):
    if headers is None:
        headers = ua
    try:
        r = requests.get(url=url, headers=headers, timeout=5)
        r.raise_for_status()
        print('Request GET successfully!')
        return BeautifulSoup(r.text, 'lxml')
    except:
        print("Request GET Failed")
def GET(url: str, headers=None):
    if headers is None:
        headers = ua
    try:
        r = requests.get(url=url, headers=headers, timeout=5)
        r.raise_for_status()
        print('Request GET successfully!')
        return etree.HTML(r.text)
        # return SelectorList.xpath(r.text)
    except:
        print("Request GET Failed")

