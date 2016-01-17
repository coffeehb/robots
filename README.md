# robots

“Robots” contains set of tools useful while web scraping. It consists of the two main modules (general and units) and some functional tests. In “general” you can find scripts useful for building scrapers. In “units” you can find custom robots, and/or helper robots (e.g. importers, which helps you to interact with import.io API). To use “robots” you need some 3rd part dependencies, ie. BeautifulSoup4 and requests. You need also add “robots” path to your python search path.

robots.general:
+ customFunctions – contains functions useful in different kind of scrapers/crawlers, eg. Extracting internal/external link or converting url to beautiful soap object.

+ headersHandler  - contains functions to handle headers which are being send along with http request. By default it sets different set of headers in each request.
+ proxyHandler – contains helper functions to handle proxies

+ requestsHandler -  main module which is used for making http requests. At the time of writing this document it has one method: http GET request. It add some custom functionality like handling headers and proxy to python requests library. Usage is exactly the same as requests.get, except defining headers and proxies argument. While using requestsHandler.get you don't need to care about headers (default functionality is to send different headers each request, which is especially useful while crawling whole domain). Also using proxies is easier. It also support proxyHarvester which is one of the main helper units.

+ resultsHandler – contains useful functions to save scrapeing results to JSON and/or CSV.

robots.units:
+ importers – helper unit to interact with import.io API
+ crawler – unit which crawl through whole domain. Currently action is not implemented yet. Right now only functionality is creation of domain sitemap

robots.units.proxyHarvester:

This unit consist of custom scrapers for site with free proxy list and main script ie. harvester. Main idea behind proxyHarvester is to get as reliable free proxy list as possible and maintaining it in real time. First thing harvester is doing is scraping all defined free proxy lists. Next, it check if each single proxy is healthy or sick. Sick proxies (most of them... free proxies are crap...) are removed from list. Healthy proxies are stored and constantly checked if still healthy. Healthy proxies are stored in python pickle file each 30s. To get as good proxy list as possible, harvester should run while whole scrapping processes. It is convenient to use requestsHandler along with harvester, as it support backup proxy definition. Status of free proxies changes all the time and it is possible that proxy defined as healthy still doesn't work properly. If backup proxy is defined, it will be ised in such a case.
