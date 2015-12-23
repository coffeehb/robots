""" Custom scraper for https://proxy-list.org/english/index.php proxylist. """
# built-in
import base64
import re
import time

# custom
from robots.general import customFunctions
from robots.general import resultsHandler

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def getProxies(url, proxies=None):
    """ Returns list of dictionaries with proxies (last update, host, port, country, type and anonymity level) from page. """

    bsObj = customFunctions.url2bs(url, proxies=proxies)
    proxiesList = []

    if bsObj:

        tableTag = bsObj.findAll('div', {'class':'table'})[0]
        proxyTags = tableTag.findAll('ul')

        for proxyTag in proxyTags[1:]:

            proxy = {}
            proxy['source'] = 'https://proxy-list.org/english/index.php'

            encodedProxyTag = proxyTag.findAll('li', {'class':'proxy'})[0].findAll('script')[0].text
            encodedProxy = re.findall(r'Proxy\(\'([\d\w=]+)\'\)', encodedProxyTag)[0]
            decodedProxy = base64ToString(encodedProxy)

            proxy['host'] = decodedProxy.split(':')[0]
            proxy['port'] = decodedProxy.split(':')[1]
            proxy['country'] = proxyTag.findAll('li', {'class':'country-city'})[0].findAll('div')[0].findAll('span')[0]['title']
            proxy['speed'] = proxyTag.findAll('li', {'class':'speed'})[0].text.strip()
            proxy['type'] = proxyTag.findAll('li', {'class':'https'})[0].text.strip()
            proxy['anonymity'] = proxyTag.findAll('li', {'class':'type'})[0].text.strip()

            proxiesList.append(proxy)

        return proxiesList


def normalize(listWithProxies):
    """ Screens and normalizes proxies to be ready to use in proxyHarvester. """

    nProxies = []
    for proxy in listWithProxies:

        nProxy = {}

        if proxy['type'] != 'HTTP' and proxy['type'] !='HTTPS':
            continue

        if proxy['anonymity'] == 'Transparent' or proxy['anonymity'] == 'Anonymous':
            continue

        nProxy['source'] = proxy['source']
        
        if proxy['type'] == 'HTTP':
            nProxy['proxy'] = 'http://{0}:{1}'.format(proxy['host'], proxy['port'])
        elif proxy['type'] == 'HTTPS':
            nProxy['proxy'] = 'https://{0}:{1}'.format(proxy['host'], proxy['port'])

        nProxies.append(nProxy)

    return nProxies


def main(proxies=None):

    pages = ['https://proxy-list.org/english/index.php?p={0}'.format(idx) for idx in range(1,11)]

    results =[]
    for page in pages:
        result = getProxies(page, proxies=proxies)
        results.extend(result)
        time.sleep(1)

    return results

if __name__ == '__main__':

    results = main()
    resultsHandler.saveResultsAsCSV(results, '/home/tulski/Desktop/proxy-list-org.csv')