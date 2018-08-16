from bs4 import BeautifulSoup
import requests
from datetime import datetime


def is_valid_url(url):
    return True if url[0:4] is None or url[0:4] == 'http'  else False


def get(url):
    if(is_valid_url(url) is False): return False

    request = requests.get(url)

    if (request.status_code != 200): return False

    plain = request.text
    s = BeautifulSoup(plain, 'html.parser')
    return s


def filter_url(url, source_url):
    if url in ['#', '/']:
        return False
    if url is None:
        return False

    search_keys = ['javascript', 'voice']

    for key in search_keys:
        if url.find(key) > -1:
            return False

    if url[0: 2] is '//':
        return 'http' + url

    print(url[0: 4])
    if url[0: 4] is 'http':
        return url
    else:
        return source_url + url


def log_error(s):
    print(datetime.now(), ": ", s)