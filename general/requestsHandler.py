# built-in
import logging
import urllib

# 3rd parts
import requests

# custom
from robots.general import headersHandler
from robots.general import proxyHandler

# configure and set up logger:
# create logger
logger = logging.getLogger('requestHandler_logger')
logger.setLevel(logging.DEBUG)

# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('[%(module)s]: %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add handler to logger
logger.addHandler(ch)

def setHeaders(option):
    """ Returns dictionary with appropriate headers, based on *option* """
    if option == 'random':
        headers = headersHandler.randomHeaders()
    else:
        try:
            headers = headersHandler.specificUserAgent(option)    
        except KeyError:
            headers = headersHandler.randomHeaders()
    return headers

def setProxy(option):
    """ Returns dictionary with appropriate proxy, based on *option*  """

    if not option:
        proxy = None

    elif isinstance(option, str):
        proxy = proxyHandler.parseProxy(option)

    elif isinstance(option, list):
        proxy = proxyHandler.randomProxyFromList(option)

    elif isinstance(option, dict):
        proxy = option

    else:
        proxy = None

    return proxy


def get(url, headers='random', proxies = None, **kwargs):
    """
        Add some functionality to requests.get.

        *headers* specifies request headers. Default is "random". You can also set specific user-agent,
        eg. "Firefox", "IE" etc. (see robots.general.headersHandler for whole list of values).

        *proxy* specifies proxy which will (or won't, which is default) be used. If proxy is string (eg: http://197.159.142.97)
        it assumes that this proxy will be used constantly. If list of proxies is specifies, random proxy from list
        will be used each request.

        You can set robots.general.proxyHandler.proxyHarvester object as a *proxies* argument. See its class definition 
        in robots.general.proxyHandler for usage details.

        **kwargs - Optional arguments that 'requests.request' takes. For details, see: http://docs.python-requests.org/en/latest/api/
    """

    if isinstance(proxies, proxyHandler.proxyHarvester):
        # proxyHarvester request is managed in slighty different way (to support back-up proxies)
        proxyList = proxies.getProxyList()
        if proxyList:
            proxy = proxyHandler.randomProxyFromList(proxyList)
        else:
            proxy = None
            r = get(url)

        if proxy:

            r = get(url, headers=headers, proxies = proxy, timeout = 8)

            if not r:
                backup = proxies.backupProxy

                if isinstance(backup, proxyHandler.proxyHarvester):
                    newRandom = proxyHandler.randomProxyFromList(proxyList)
                    r = get(url, headers=headers, proxies = newRandom, timeout = 8)
                else:
                    r = get(url, headers=headers, proxies = backup, timeout = 8)

                if r:
                    return r

            else:
                return r


    # set headers
    headers_ = setHeaders(headers)

    # set proxy
    proxy_ = setProxy(proxies) # proxy_ has correct for requests library format

    # do actual request
    try:
        if url.startswith('//'):
            url = url.replace('//', 'http://')
        
        if url.startswith('file://'):
            # if local file ('requests' library do not handle them)
            logger.info('Opening local file... ({0})'.format(url))
            r = urllib.request.urlopen(url)
        else:
            if proxies:
                logger.debug('Sending GET request to: {0} [ip: {1}]'.format(url, proxies))
            else:
                logger.debug('Sending GET request to: {0} [ip: {1}]'.format(url, 'no proxy'))
            r = requests.get(url, headers=headers_, proxies=proxy_, **kwargs)
            logger.debug('Got response from {0}. Status: {1}'.format(url, r.status_code))

    # network problem (e.g. DNS failure, refused connection, etc)
    except requests.exceptions.ConnectionError:
        logger.debug('ConnectionError while sending request to: "{0}"'.format(url))
        return None

    # invalid HTTP response
    except requests.exceptions.HTTPError:
        logger.debug('Invalid response from: "{0}"'.format(url))
        return None

    # request times out
    except requests.exceptions.Timeout:
        logger.debug('Waiting too long for response from: "{0}"'.format(url))
        return None

    # request exceeds the number of maximum redirections
    except requests.exceptions.TooManyRedirects:
        logger.debug('Too many redirections while sending request to: "{0}"'.format(url))
        return None

    # no schema (http:// etc.) at the begining of url 
    except requests.exceptions.MissingSchema as e:
        logger.debug(e)
        return None

    # schema is not handled by requests library
    except requests.exceptions.InvalidSchema as e:
        logger.debug(e, '({0})'.format(url))
        return None

    # others not specified exceptions, eg: ConnectionResetError
    except Exception as e:
       logger.debug('{0} ({1}, while sending request to: {2}. Traceback below:)'.format(e, type(e).__name__, url), exc_info=True)
       return None

    return r



"""
TODO:
- change prints to logging
- POST function

It woulb be nice to have:
- 
"""