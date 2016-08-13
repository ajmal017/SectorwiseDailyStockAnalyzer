from urllib.request import urlopen
from bs4 import BeautifulSoup


def getFinviz(base_url):

    initIttr = 20
    k = 1
    done = False
    url = base_url
    info = []

    try:
        html = urlopen(url).read()
        done = False
    except:
        done = True

    while (not done):
        soup = BeautifulSoup(html, "html.parser")

        data = []
        new_info = []
        for link in soup.find_all('a'):
            data.append(link.get('href'))

        for element in list(set(data)):
            if "quote.ashx?t=" in element:
                new_info.append(element[element.find("?t=") + 3:element.find("&ty")])

        if info and new_info[-1] == info[-1]:
            break
        for each_element in new_info:
            info.append(each_element)

        url = base_url + "&r=" + str(k * initIttr + 1)
        k = k + 1
        try:
            html = urlopen(url).read()
        except:
            done = True

    return set(info)
