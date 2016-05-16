""" Custom scraper for hidemyass proxylist site. """
# built-in
import re
import time

# custom
import custom

def getPagination(url, proxies=None):
    """ Return url to all pages """
    bsObj = custom.url2bs(url, proxies=proxies)

    if bsObj:
        try:
            pagesTag = bsObj.findAll('ul', {'class':'pagination ng-scope'})[0]
        except IndexError:
            return []
        links = custom.get_internal_links(pagesTag)
        pages = [custom.rel2abs(link, url) for link in links]

    pages.insert(0, url)
    return pages


def decipherProxy(hostTag):
    """ Deciphers tags styling and returns proper proxy host """
    host  = []
    styles = hostTag.findAll('style')[0].text
    pattern = re.compile(r'\.([\w\d\-]+)\{display:inline\}')
    visible = re.findall(pattern, styles)

    for tag in hostTag:

        if tag.__class__.__name__ == 'Tag':

            if tag.has_attr('class') and tag['class'][0] in visible:
                host.append(tag.text)

            elif tag.has_attr('class') and re.search(r'^\d+$', tag['class'][0]):
                host.append(tag.text)

            elif tag.has_attr('style') and 'inline' in tag['style']:
                host.append(tag.text)
        
            elif tag.has_attr('style') and re.search(r'^\d+$', tag['style']):
                host.append(tag.text)

        elif tag.__class__.__name__ == 'NavigableString':
            host.append(tag)
        
    return (''.join(host))

def getProxies(url, proxies=None):
    """ Returns list of dictionaries with proxies (last update, host, port, country, type and anonymity level) from page. """

    bsObj = custom.url2bs(url, proxies=proxies)
    proxiesList = []

    if bsObj:

        try:
            tableTag = bsObj.findAll('section', {'class':'proxy-results section-component'})[0]
        except IndexError:
            return []

        proxyTags = tableTag.findAll('tr')

        for proxyTag in proxyTags[1:]:

            columns = proxyTag.findAll('td')
            proxy = {}
            proxy['source'] = 'http://proxylist.hidemyass.com/'
            proxy['lastUpdate'] = columns[0].text.strip()
            proxy['host'] = decipherProxy(columns[1].findAll('span')[0])
            proxy['port'] = columns[2].text.strip()
            proxy['country'] = columns[3].text.strip()
            proxy['speed'] = re.findall(r'\d+%', columns[4].findAll('div', {'class':'indicator'})[0]['style'])[0]
            proxy['type'] = columns[6].text.strip()
            proxy['anonymity'] = columns[7].text.strip()
            proxiesList.append(proxy)

        return proxiesList

def normalize(listWithProxies):
    """ Screens and normalizes proxies to be ready to use in proxyHarvester. """

    nProxies = []
    for proxy in listWithProxies:

        nProxy = {}

        if proxy['type'] != 'HTTP' and proxy['type'] !='HTTPS':
            continue

        if proxy['anonymity'] != 'High +KA' and proxy['anonymity'] != 'High':
            continue

        if int(proxy['speed'].replace('%', '')) < 50:
            continue

        nProxy['source'] = proxy['source']
        
        if proxy['type'] == 'HTTP':
            nProxy['proxy'] = 'http://{0}:{1}'.format(proxy['host'], proxy['port'])
        elif proxy['type'] == 'HTTPS':
            nProxy['proxy'] = 'https://{0}:{1}'.format(proxy['host'], proxy['port'])

        nProxies.append(nProxy)

    return nProxies


def main(proxies=None):
    """ Main function. Returns list of proxies from all pages on hidemyass.com."""
    url = 'http://proxylist.hidemyass.com/'
    pages = getPagination(url, proxies=proxies)
    results =[]

    for page in pages:
        results.extend(getProxies(page, proxies=proxies))
        time.sleep(1)

    return results

if __name__ == '__main__':
    main()
