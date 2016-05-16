# built- in
import os
import pickle
import random
import re


class ProxyHarvester():
    """
        Class which servs as interface to use proxyHarvester. *fullpath* is path to python pickle where
        proxies from proxyHarvester are being saved. *backupProxy* is proxy which will be used if main proxy
        fail. Reason for that is bad reliabilty of free proxies....

        backupProxy can be None, constant proxy (string), random from list (list) or even the same proxyHarvester
        object used as a main proxy. In that case another proxy from scraped proxies will be chosen. It is not 
        recomended to use proxyharvester as a backupProxy, because of low reliability of free proxies.

        Although it is obvious, please remember that proxyHarvester must be working while using this interface.
    """

    def __init__(self, fullpath, backupProxy=None):
        self.path2pickle = fullpath
        self.backupProxy = backupProxy

    def get_proxy_list(self):
        """ Gets proxies from pickle. """
        
        if os.path.exists(self.path2pickle) == True:
            proxyList = list(pickle.load(open(self.path2pickle, 'rb')))
        else:
        	proxyList = None

        if proxyList and len(proxyList) > 0:
            return proxyList


def parse_proxy(proxyAsString):
    """ Rerurns dictionary with correctly formated (for "requests" library) proxy. """
    #eg: http://10.10.1.10:3128
    pattern1 = re.compile(r'^(https?)://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$')

    #eg: http://user:pass@10.10.1.10:3128
    pattern2 = re.compile(r'^(https?)://(.*):(.*)@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$')

    if re.match(pattern1, proxyAsString):

        matchObj = re.match(pattern1, proxyAsString)
        (protocol, host, port) = (matchObj.group(1), matchObj.group(2), matchObj.group(3))

        return {protocol : '{0}://{1}:{2}'.format(protocol, host, port)}

    elif re.match(pattern2, proxyAsString):

        matchObj = re.match(pattern2, proxyAsString)
        (protocol, user, pwd, host, port) = (matchObj.group(1), matchObj.group(2), matchObj.group(3), matchObj.group(4), matchObj.group(5))

        return {protocol : '{0}://{1}:{2}@{3}:{4}'.format(protocol, user, pwd, host, port)}

    else:
        raise re.error('Couldn\'t parse proxy: {0}. String be should be in format like eg: http://10.10.1.10:3128 or http://user:pass@10.10.1.10:3128'.format(proxyAsString))


def random_proxy_from_list(ListOfProxies):
    """
        Pick random proxy from list and dictionary with correctly formated (for "requests" library) proxy.
        Proxies should have type in the begining and port in the end, eg: http://197.159.142.97:2225
    """

    proxy = random.choice(ListOfProxies)
    return parse_proxy(proxy)