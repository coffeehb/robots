# built in
import re
import unittest

# custom
from robots.general import proxyHandler

class proxyTest(unittest.TestCase):

    def test_parseProxy(self):

        prox1 = "https://10.10.1.10:3128"
        prox2 = "http://user:pass@10.10.1.10:3128"

        res1 = proxyHandler.parseProxy(prox1)
        res2 = proxyHandler.parseProxy(prox2)

        assert(res1 == {'https':"https://10.10.1.10:3128"})
        assert(res2 == {'http':"http://user:pass@10.10.1.10:3128"})
        with self.assertRaises(re.error):
            res3 = proxyHandler.parseProxy('not.valid.proxy.format')



if __name__ == '__main__':
    unittest.main()