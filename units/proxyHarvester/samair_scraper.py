""" Custom scraper for http://www.samair.ru proxylist site. """

# built-in
import re
import time

# custom
from robots.general import customFunctions
from robots.general import resultsHandler
from robots.general import requestsHandler

def getStyles(proxies=None):
    """ Get styles to read hidden port information """

    url = 'http://www.samair.ru/proxy/proxy-01.htm'


    # request to get link to styles (it changes all the time - needs to be obtained dnamically)
    r = requestsHandler.get(url, proxies=proxies)

    if r.status_code == 200:
        pattern = re.compile(r'/styles/[\w\d]+\.css')
        stylesUrlRel = re.findall(pattern, r.text)[0]
        stylesUrl = customFunctions.rel2abs(stylesUrlRel, url)

        # get styles
        bsObj = customFunctions.url2bs(stylesUrl)
        if bsObj:
            pattern = r'\.([\d\w]+):after {content:"(\d+)"}'
            matches = re.findall(pattern, bsObj.text)
            styles = {match[0]:match[1] for match in matches}

        return styles


def getProxies(url, styles, proxies=None):
    """ Returns list of dictionaries with proxies (last update, host, port, country, type and anonymity level) from page. """

    bsObj = customFunctions.url2bs(url, proxies=proxies)
    proxiesList = []

    if bsObj:

        tableTag = bsObj.findAll('table', {'id':'proxylist'})[0]
        proxyTags = tableTag.findAll('tr')

        for proxyTag in proxyTags[1:]:

            try:
                columns = proxyTag.findAll('td')
                proxy = {}
                proxy['source'] = 'http://www.samair.ru/proxy/'
                proxy['country'] = columns[3].text.strip()
                proxy['anonymity'] = columns[1].text.strip()
                proxy['lastUpdate'] = columns[2].text.strip()

                proxy['host'] = columns[0].findAll('span')[0].text.replace(':', '').strip()
                portClass = columns[0].findAll('span')[0]['class'][0]
                proxy['port'] = styles[portClass]
                proxiesList.append(proxy)
            except KeyError:
                continue

        return proxiesList


def normalize(listWithProxies):
    """ Screens and normalizes proxies to be ready to use in proxyHarvester. """

    nProxies = []
    for proxy in listWithProxies:

        nProxy = {}

        if proxy['anonymity'] != 'high-anonymous':
            continue

        nProxy['source'] = proxy['source']
        nProxy['proxy'] = 'http://{0}:{1}'.format(proxy['host'], proxy['port'])
        
        nProxies.append(nProxy)

    return nProxies


def main(proxies=None):
    """ Main function. Returns list of proxies from all pages on http://www.samair.ru."""

    styles = getStyles(proxies=proxies)
    time.sleep(2)

    pages01_10 = ['http://www.samair.ru/proxy/proxy-0{0}.htm'.format(idx) for idx in range(1,10)]
    pages10_30 = ['http://www.samair.ru/proxy/proxy-{0}.htm'.format(idx) for idx in range(10,31)]
    pages = pages01_10 + pages10_30

    results =[]
    for page in pages:
        result = getProxies(page, styles)
        results.extend(result)
        time.sleep(1)

    return results

if __name__ == '__main__':
    results = main()
    #normalize(results)

    for result in results:
        print(result['host']+':'+result['port'])