import requests
# from urllib.request import Request, urlopen
from urllib2 import urlopen
from bs4 import BeautifulSoup
# from urllib.error import  URLError
import time
# import http.client # for Python 3.x
import httplib # for Python 2.7.x
from requests import get  # to make GET request

def download(url):
    # open in binary mode
     response = get(url)
     return response.content

def getFinviz(base_url):

    initIttr = 20
    k = 1
    done = False
    url = base_url
    info = []

    html = download(url)

    while (not done):
        soup = BeautifulSoup(html, "html.parser")

        data = []
        new_info = []
        for link in soup.find_all('a'):
            data.append(link.get('href'))

        for element in list(set(data)):
            if "quote.ashx?t=" in element:
                new_info.append(element[element.find("?t=") + 3:element.find("&ty")])

        # print("new_info: ", new_info)
        # print("info: ", new_info)
        # time.sleep(1)
        if info and new_info[-1] == info[-1]:
            break
        for each_element in new_info:
            info.append(each_element)

        url = ''.join((base_url.rstrip('\n'),"&r=",str(k * initIttr + 1)))
        # print("URL: ", url)
        k = k + 1

        # print("Still working on GET: ", k)
        html = []
        html = download(url)

    return set(info)
