import requests
#from robots.units.proxyHarvester import hideMyAss_scraper

url = 'http://icanhazip.com'

#proxyList = hideMyAss_scraper.main()

# idx = 0
# while True:
# 	if proxyList[idx]['type'] == 'HTTP':
# 		host = proxyList[idx]['host']
# 		port = proxyList[idx]['port']
# 		break
# 	else:
# 		idx += 1

host = '185.128.36.17'
port = '80'


proxy = {'http' : 'http://{0}:{1}'.format(host, port)}
print('proxy -> '+ proxy['http'])

r = requests.get(url, proxies = proxy)
print('req with proxy -> '+r.text)

r2 = requests.get(url)
print('req without proxy -> '+r2.text)
