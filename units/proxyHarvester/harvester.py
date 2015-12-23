# built-in
import logging
import os
import pickle
import random
import re
import requests
import tempfile
import threading
import time
from queue import Queue

# custom
from robots.general import requestsHandler
from robots.general import customFunctions
from robots.general import proxyHandler

# scrapers
from robots.units.proxyHarvester import hideMyAss_scraper
from robots.units.proxyHarvester import proxy_list_org_scraper
from robots.units.proxyHarvester import free_proxy_list_net_scraper
from robots.units.proxyHarvester import samair_scraper


class Collectioner(threading.Thread):
    """
        Collectioner is responsible for scrapeing proxies. As argument during initialization
        it takes custom scrapers for website with free proxy lists. 

        It uses global variable (listOfScrapers)
        were custom scrapers (for websites with free proxy lists) are listed.
    """
    
    def __init__(self, scraper):
        threading.Thread.__init__(self)

        self.name = 'Collect - {0}'.format(listOfScrapers.index(scraper)+1)
        self.setDaemon(True)
        self.scraper = scraper

    def run(self):
        logger.debug('Collectioner start collecting...')
        self.collect()

    def collect(self):
        proxyHarvesterObj = proxyHandler.proxyHarvester('proxies.p') # Uses itself if scraped proxies are available. If not, no proxies are used while scrapeing
        extractedProxies = self.scraper.main(proxies=proxyHarvesterObj)
        proxies = self.scraper.normalize(extractedProxies)
        [uncheckedProxy.put(proxy['proxy']) for proxy in proxies]
        logger.debug('Got proxies from {0}. NumOfProxies: {1}'.format(proxies[0]['source'], len(proxies)))


class QualityController(threading.Thread):
    """
        QualityController is resposible for checking if proxy aspires to be healthy. It uses uncheckedProxy queue
        to get candidates proxies. Then check their qulity using checkProxy function (which is not implemented
        as object method, but rather module funtion). If proxy is healthy it moves it to healthyProxy queue.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'QualCont: {0}'
        self.setDaemon(True)

    def run(self):

        while not uncheckedProxy.empty():
            proxy = uncheckedProxy.get()
            proxyStatus = checkProxy(proxy)
            if proxyStatus == True:
                healthyProxy.put(proxy)
                proxiesSet.add(proxy)
            uncheckedProxy.task_done()


class Mainteiner(threading.Thread):
    """
       Mainteiner object is resposible for checking proxies inside healthyProxy. If proxy is still healthy it
       puts proxy again to the queue. Otherwise proxy is remove from queue as well from results (proxiesSet)

       As it is right now, there should be only one Mainteiner. To better support of multiple Mainteiners there
       should be implemented locking mechanism while removeing proxies from proxiesSet.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'Mainteiner'

    def run(self):

        while True:
            if healthyProxy.empty():
                break
            else:
                proxy = healthyProxy.get()
                proxyStatus = checkProxy(proxy)
                if proxyStatus == True:
                    healthyProxy.put(proxy)
                else:
                    # removes proxy from results set. Assumes that there is only one Mainteiner thread
                    # if there would be more Mainteiners, you should implement lock/aquire system.
                    try:
                        proxiesSet.remove(proxy)
                    except KeyError: # eg. if two same proxies in queue (in set will be only one, hence error can occure)
                        pass 
                healthyProxy.task_done()
            time.sleep(4)


class Farmer(threading.Thread):
    """
        Farmer object is responsible for whole proccess of collecting and checkig proxies.
        It first scrape all proxies using separate Collectioner object for each scraper from
        listOfScrapers global variable. After scrapeing is finished, it starts QualityController 
        to check proxies.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'Farmer'
        self.setDaemon(True)

    def run(self):
        collectioners = [Collectioner(scraper) for scraper in listOfScrapers]
        [col.start() for col in collectioners]
        [col.join() for col in collectioners]

        controllers = [QualityController() for i in range(20)]
        [qc.start() for qc in controllers]
        [qc.join() for qc in controllers]


def checkProxy(proxy):
    """ 
        Send request using proxy to one of the checkPoints, ie. website where you can check your Ip addreess.
        If proxy is healthy (response from checkPoint match to proxy) returns True, else False.
    """

    checkPoints = ['http://icanhazip.com',
                   'https://www.whatismyip.com/',
                   'http://mxtoolbox.com/WhatIsMyIP/',
                   'http://whatismyipaddress.com/',
                   'http://www.checkip.com/',
                   'http://checkip.dyndns.org/',
                   'http://www.ipchicken.com/']
    
    host = proxy.replace('http://', '').replace('https://', '').split(':')[0]

    try:
        r = requestCheck(random.choice(checkPoints), proxy)
    except:
        r = None

    if r and r == host:
        logger.debug('{0} is healty'.format(host))
        return True
    else:
        logger.debug('{0} is sick [got: {1}]'.format(host, r))
        return False
        

def requestCheck(checkPoint, proxy):
    """
        Helper for checkProxy function. Scrape response from checkPoint and compare it with
        proxy. DO NOT handel exceptions. Those are handled generally in checkProxy func.
    """

    bsObj = customFunctions.url2bs(checkPoint, proxies=proxy, timeout=5)

    if not bsObj:
        return None

    if checkPoint == 'http://icanhazip.com':
        return bsObj.text.strip()
        
    elif checkPoint == 'https://www.whatismyip.com/':
        ipTag = bsObj.findAll('div', {'class':'ip'})[0]
        ipParts = ipTag.findAll(['label', 'span'])
        ip = ''
        for part in ipParts:
            ip += part.text
        return ip
        
    elif checkPoint == 'http://mxtoolbox.com/WhatIsMyIP/':
        ipTag = bsObj.findAll('a', {'id':'ctl00_ContentPlaceHolder1_hlIP'})[0]
        return ipTag.text
        
    elif checkPoint == 'http://whatismyipaddress.com/':
        pattern = re.compile(r'//whatismyipaddress.com/ip/\d+\.\d+\.\d+\.\d+')
        ipTag = bsObj.findAll('a', {'href':pattern})[0]
        return ipTag.text
        
    elif checkPoint == 'http://www.checkip.com/':
        ipTag = bsObj.findAll('div', {'id':'ip'})[0].findAll('span')[0]
        return ipTag.text

    elif checkPoint == 'http://checkip.dyndns.org/':
        pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        ip = re.findall(pattern, bsObj.text)[0]
        return ip

    elif checkPoint == 'http://www.ipchicken.com/':
        pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        ip = bsObj.findAll(text=pattern)[0].strip()
        return ip


def main(fullpath):
    """ Main routine. *fullpath* determines where pickle with proxies will be stored. """

    ts1 = time.time()
    ts2 = time.time()
    fullpath = fullpath
    while True:

        aliveThreads = [t.getName() for t in threading.enumerate()]

        # there is less than 20 healthy proxy and Farmer is not on harvest
        if healthyProxy.qsize() < 20 and 'Farmer' not in aliveThreads:
            logger.info('There is less than 20 hea proxies. Start harvesting')

            farmer = Farmer()
            farmer.start()

        # there is less than 20 healthy proxies but Farmer has already started harvesting
        elif healthyProxy.qsize() < 20 and 'Farmer' in aliveThreads:
            logger.info('There is less than 20 healty proxies. A farmer is already on the harvest. Wait for a while...')
            time.sleep(8)

        # more than 20 healt proxies, nut there is no Mainteiner
        elif healthyProxy.qsize() > 20 and 'Mainteiner' not in aliveThreads:
            mainteiner = Mainteiner()
            mainteiner.start()

        # save pickle with result healthy proxy
        elif time.time() - ts1 > 30:

            with tempfile.NamedTemporaryFile('wb', dir=os.path.dirname(fullpath), delete=False) as tf:
                pickle.dump(proxiesSet, tf)
                tempname = tf.name
            os.rename(tempname, fullpath)  
            ts1 = time.time()

        # log healthyProxy size
        elif time.time() - ts2 > 100:
            logger.info('Currently there are {0} healthy proxies'.format(healthyProxy.qsize()))
            ts2 = time.time()


# configure and set up logger:
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('(%(threadName)-12s) %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add handler to logger
logger.addHandler(ch)


uncheckedProxy = Queue()
healthyProxy = Queue()
proxiesSet = set() # resulting set with proxies

# list with custom scrapers of websites where free proxy lists are present
listOfScrapers = [hideMyAss_scraper,
                  proxy_list_org_scraper,
                  free_proxy_list_net_scraper,
                  samair_scraper]

if __name__ == '__main__':
    fullpath = os.path.join(os.path.dirname(__file__), 'proxies.p')
    main(fullpath)

"""
TODO:

- implement using proxies to scrpape proxies
- chreate better logging mechanism (I want to have multiple different loggers in each file in robots module)

"""