""" Custom scraper for https://free-proxy-list.net/ proxylist. """

# custom
import custom

def getProxies(url, proxies = None):
    """ Returns list of dictionaries with proxies along with their (last update, host, port, country, type and anonymity level). """

    bsObj = custom.url2bs(url, proxies=proxies)
    proxiesList = []

    if bsObj:

        tableTag = bsObj.findAll('tbody')[0]
        rows = tableTag.findAll('tr')

        proxies = []
        for row in rows:
            columns = row.findAll('td')
            proxy = {}
            proxy['source'] = 'https://free-proxy-list.net/'
            proxy['lastUpdate'] = columns[7].text.strip()
            proxy['host'] = columns[0].text.strip()
            proxy['port'] = columns[1].text.strip()
            proxy['country'] = columns[3].text.strip()
            type_ = columns[6].text.strip()
            if type_ == 'yes':
                proxy['type'] = 'HTTPS'
            elif type_ == 'no':
                proxy['type'] = 'HTTP'

            proxy['anonymity'] = columns[4].text.strip()
            proxy['speed'] = 'unknown'
            proxiesList.append(proxy)

        return proxiesList

def normalize(listWithProxies):
    """ Screens and normalizes proxies to be ready to use in proxyHarvester. """

    nProxies = []
    for proxy in listWithProxies:

        nProxy = {}

        if proxy['type'] != 'HTTP' and proxy['type'] !='HTTPS':
            continue

        if proxy['anonymity'] == 'transparent' or proxy['anonymity'] == 'anonymous':
            continue

        nProxy['source'] = proxy['source']
        
        if proxy['type'] == 'HTTP':
            nProxy['proxy'] = 'http://{0}:{1}'.format(proxy['host'], proxy['port'])
        elif proxy['type'] == 'HTTPS':
            nProxy['proxy'] = 'https://{0}:{1}'.format(proxy['host'], proxy['port'])

        nProxies.append(nProxy)

    return nProxies

def main(proxies = None):
    """ Main function. Returns list of proxies from free-proxy-list.net. """
    
    url = 'https://free-proxy-list.net/'
    results = getProxies(url, proxies = proxies)
    return results

if __name__ == '__main__':
    main()
