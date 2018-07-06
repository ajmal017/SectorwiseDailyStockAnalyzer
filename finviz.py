import requests
# from urllib2 import urlopen
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import re
# import http.client # for Python 3.x
# import httplib # for Python 2.7.x
# import httplib.client # for Python 3.6.x
from requests import get  # to make GET request

template = "body=\[<img src='chart\.ashx\?s=m&ty=c&t=(.*)\'>.*quote.*&nbsp;(.*) \|.*\|.*"

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
    last_stock = []

    html = download(url)
    stock_sub_sector = re.findall(template, html)

    while (not done):
        # soup = BeautifulSoup(html, "html.parser")

        data = []
        # new_info = []
        # for link in soup.find_all('a'):
        #     data.append(link.get('href'))

        # for element in list(set(data)):
        #     if "quote.ashx?t=" in element:
        #         new_info.append(element[element.find("?t=") + 3:element.find("&ty")])


        # filter out exhange traded funds
        for each_element in stock_sub_sector:
            if not 'Exchange Traded Fund' in each_element[1]:
                info.append(each_element[0])

        # loop end condition
        if info and last_stock and info[-1] == last_stock:
            break

        # print "info: ", info

        url = ''.join((base_url.rstrip('\n'),"&r=",str(k * initIttr + 1)))
        k += 1
        # print "url: ", url

        last_stock = info[-1]
        # print "last_stock: ", last_stock

        html = []
        html = download(url)
        stock_sub_sector = re.findall(template, html)

    return sorted(set(info))
