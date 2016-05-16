# built-in
import re
from urllib.parse import urljoin, urlparse

# 3rd part
from bs4 import BeautifulSoup as bs

# custom
import useragents
import requestshandler


def url2bs(url, headers='random', proxies=None, timeout=5):
    """
       Convert plain url to bsObj. First sends request and if everything is ok parse html and retruns bsObj.
       If there is no response returns None. *headers* specify request headers. Default is "random". 
       You can also set specific user-agent,  eg. "Firefox", "IE" etc. (see robots.general.headersHandler 
       for user-agents list).
    """

    # if user pass bsObj instead of url -> return itself
    if isinstance(url, bs):
        return url

    # get page
    r = requestshandler.get(url, headers=headers, proxies=proxies, timeout=timeout)

    if r:
        try:
            html = r.text
        except AttributeError:
            # response comes from urllib not requests library
            html = r.read()

        bsObj = bs(html, 'html.parser')
        return bsObj

    else:
        return None

def get_internal_links(bsObj, includeUrl=None, unwantedExts=('js', 'css')):
    """ 
        Gets all internal links on page.
        TODO: should avoid honeypots for scrapers like hidden links 
    """

    if not bsObj:
        return

    internalLinks = []
    if includeUrl:
        pattern = re.compile('^(/[^/]|.*'+includeUrl+')')
    else:
        pattern = re.compile('^/[^/]')
    tags = bsObj.findAll(lambda tag: 'href' in tag.attrs)
    for tag in tags:
        href = tag.attrs['href']
        if href != None and re.search(pattern, href) != None:
            if not href.endswith(unwantedExts) and href not in internalLinks:
                internalLinks.append(href)
        else:
            continue

    return internalLinks

def rel2abs(relativeUrl, mainUrl):
    """ 
        Converts relative url to absolute url path.
        It joins base of *mainUrl* with *relativeUrl* 
    """

    baseUrl = urlparse(mainUrl).netloc
    return urljoin(mainUrl, relativeUrl)