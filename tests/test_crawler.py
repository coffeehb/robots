# built-in
import os
import sys
import unittest

# 3rd part
from bs4 import BeautifulSoup as bs

# custom
from robots.units import crawler
from robots.general import customFunctions

class CrawlerTest(unittest.TestCase):

    def test_url2bs(self):
        """ Checks if exception is handled when sth wrong with url """
        assert(customFunctions.url2bs('http://www.non-existing.none') == None)
        assert(customFunctions.url2bs('www.non-existing.none') == None)

    def test_getInternalLinks(self):
        sitepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'site1.html')
        url = 'file://'+sitepath

        testCrawler = crawler.InternalCrawler(url, 'site1')
        internalLinks = testCrawler.getLinks(testCrawler.startUrl, baseURL='site1')
        resultAsSet = set(internalLinks)

        assert(len(internalLinks)==5)
        assert("/first/internal" in resultAsSet)
        assert("/pasta-kfe/menu/marseille-5eme-13005" in resultAsSet)
        assert("/third/internal" in resultAsSet)
        assert("www.site1.none" in resultAsSet)
        assert("//site1.exclude.com" in resultAsSet)

        testCrawler2 = crawler.InternalCrawler(url, None)
        internalLinks2 = testCrawler2.getLinks(testCrawler2.startUrl)
        resultAsSet2 = set(internalLinks2)
        assert(len(internalLinks2)==3)
        assert("/first/internal" in resultAsSet)
        assert("/pasta-kfe/menu/marseille-5eme-13005" in resultAsSet)
        assert("/third/internal" in resultAsSet)

    def test_mapsite(self):
        url = 'imretendingurl'

        visitedPages = [
                         'net1/loc1/loc2/loc3/loc4',
                         'net1/loc1/loc2/loc3/loc5',
                         'net1/loc1/loc2/loc3/loc6',
                         'net1/loc1/loc2/aaa',
                         'net1/loc1/bbb',
                         'net1/loc1/ccc',
                         'net1/x',
                         'net1/y',
                         'net1/z',
                         'net1/y/loc7',
                         'net2/loc1/loc2/loc3/loc4',
                         'net2/loc1/loc2/loc3/loc4',
                         'net3/loc1/loc2/loc3/loc4'
                        ]

        testCrawler = crawler.InternalCrawler(url, None)
        sitemap = testCrawler.mapsite(visitedPages)

        assert(len(sitemap.keys())==3)
        assert(len(sitemap['net1'])==4)
        assert(len(sitemap['net2'])==1)
        assert(len(sitemap['net3'])==1)
        assert(len(sitemap['net1']['loc1'])==3)
        assert(len(sitemap['net1']['loc1']['loc2'])==2)
        for key in ['loc1', 'x', 'y', 'z']:
            assert(key in sitemap['net1'])
        assert(len(sitemap['net2']) == 1)
        assert(len(sitemap['net3']) == 1)
        assert(sitemap['net3']['loc1']['loc2']['loc3']['loc4'] == {})

    def test_getExternalLinks(self):
        sitepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'site1.html')
        url = 'file://'+sitepath

        testCrawler = crawler.ExternalCrawler(url)
        externalLinks = testCrawler.getLinks(testCrawler.startUrl)
        resultAsSet = set(externalLinks)

        assert(len(externalLinks)==5)
        assert('www.None1.site.con' in resultAsSet)
        assert('https://testMeRobot.edu.pl' in resultAsSet)
        assert('www.site1.none' in resultAsSet)
        assert('//site1.exclude.com' in resultAsSet)
        assert('//second/internal(?)' in resultAsSet)

if __name__ == '__main__':
    unittest.main()

