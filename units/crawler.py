# built-in
import csv
import json
import logging
import sys
import time
from urllib.parse import urljoin, urlparse
import random

# custom
from robots.general import customFunctions


class Crawler():
    """ Base class for InternalCrawler and ExternalCrawler. """

    def __init__(self, startUrl):
        self.startUrl = startUrl
        self.visited = set()
        self.unwantedExtensions = ['.tif', '.tiff', '.gif',
                                    '.jpeg', '.jpg', '.jif',
                                    '.jfif', '.jp2', '.jpx',
                                    '.j2k', '.j2c', '.fpx',
                                    '.pcd', '.png', '.pdf',
                                    'ico', 'js', 'css' ]
        self.logFile = None
        sys.setrecursionlimit(2000)

    def crawl(self, url, action=None, headers='random', proxies=None):
        """ Crawling procedure """

        if not url in self.visited:
            logger.info(url)
            self.visited.add(url)
            links = self.getLinks(url, headers = headers, proxies = proxies)
            
            # handling delays between requests
            time.sleep(1)
            randomNum = random.randint(1,10)
            if randomNum >= 8:
                time.sleep(random.uniform(2, 16))

            if self.logFile:
                self.logFile.warning('Visited: {0}'.format(url))
                self.logFile.warning('Find there following links: {0}'.format(links))

        if links:
            for link in links:
                if not link in self.visited:
                    self.crawl(link, action=action, headers=headers, proxies=proxies)


class InternalCrawler(Crawler):
    """ Follows only internal links on pages. """

    def __init__(self, startUrl, base):
        Crawler.__init__(self, startUrl)
        self.base = base
        self.baseURL = urlparse(startUrl).scheme + '://'  + urlparse(startUrl).netloc

    def getLinks(self, url, baseURL = None, headers = 'random', proxies=None):
        """ Return list of available links inside given url """
        bsObj = customFunctions.url2bs(url, headers = headers, proxies=proxies)
        
        if not baseURL:
            baseURL = self.baseURL
        else:
            baseURL = baseURL

        if bsObj:
            links = [urljoin(baseURL, link) for link in customFunctions.getInternalLinks(bsObj, includeUrl=self.base, unwantedExts=tuple(self.unwantedExtensions))]
            return links

    def mapsite(self, visitedPages = None):
        """ Creates sitemap from crowled sites. As input takes log file from crawl. """

        if not visitedPages:
            visited = self.visited
        else:
            visited = visitedPages

        sitemap = {}
        for link in visited:
            pth = urlparse(link).netloc + urlparse(link).path
            customFunctions.maplinks(sitemap, pth)
        return sitemap


class ExternalCrawler(Crawler):
    """ Follows only external links on pages. """

    def __init__(self, startUrl):
        Crawler.__init__(self, startUrl)
        self.visited_netlocs = set()

    def getLinks(self, url, headers = 'random', proxies=None):
        """ Return list of available links inside given url """
        baseURL = urlparse(url).netloc
        logger.info(baseURL)
        if not baseURL in self.visited_netlocs:
            self.visited_netlocs.add(baseURL)
            bsObj = customFunctions.url2bs(url, headers = headers, proxies=proxies)
            if bsObj:
                links = customFunctions.getExternalLinks(bsObj, excludeUrl=baseURL, unwantedExts=tuple(self.unwantedExtensions))
                return links


def setLogFile(crawler = None, logFullPath=None):
    """ 
        Sets appropriate logger as a logFile *crawler* attribute. If *logFullPath* is not specified, logFile is saved to 
        present working directory with timestamp as a name. 
    """
    if not crawler:
        return
    else:
        crawler_ = crawler
        crawler.logFile = logging.getLogger('{0}_FileLogger'.format(crawler_.startUrl))

    if not logFullPath:
        logFullPath_ = '{0}.log'.format(time.time())
    else:
        logFullPath_ = logFullPath

    # create file handler and formatter
    fh = logging.FileHandler('{0}'.format(logFullPath_))
    fh.setLevel(logging.WARNING)
    fh_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # add formater to handler
    fh.setFormatter(fh_formatter)
    # add handler to formatter
    crawler.logFile.addHandler(fh)



# configure and set up console logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(ch_formatter)

logger.addHandler(ch)


"""
TODO:

- implement action

"""


if __name__ == '__main__':

    # some test urls...
    # url = 'https://www.skipthedishes.com/'
    # url = 'https://www.hungry.dk/'
    url = 'https://www.foodora.es/'

    testCrawler = InternalCrawler(url, 'foodora.es')
    setLogFile(crawler = testCrawler)
    testCrawler.crawl(testCrawler.startUrl, action=None)
    
    sitemap = testCrawler.mapsite()
    print(json.dumps(sitemap, indent=4))