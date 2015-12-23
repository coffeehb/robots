# built-in
import csv
import os
import unittest

# custom
from robots.general import resultsHandler

class resultsTest(unittest.TestCase):

    def test_json2list(self):
        json1 = {'name':'test1', 'price':40}
        list1 = resultsHandler.json2list(json1)
        assert(isinstance(list1, list))
        assert(list1 == ['test1', 40] or list1 == [40, 'test1'])

        json2 = {'items':['item1','item2'], 'prices':[{'value':40, 'currency':'USD'}, {'value':32, 'currency':'Euro'}]}
        list2 = resultsHandler.json2list(json2)
        assert(isinstance(list2, list))
        assert(len(list2) == 2)
        assert(['item1','item2'] in list2)
        assert([{'value':40, 'currency':'USD'}, {'value':32, 'currency':'Euro'}] in list2)

        json3 = {'last_name':'Tulski','age':'26','first_name':'Slawomir', 'occupation':'Programmer'}
        schema = ['first_name','last_name','age', 'occupation']
        list3 = resultsHandler.json2list(json3, schema=schema)
        assert(list3 == ['Slawomir', 'Tulski', '26', 'Programmer'])
        with self.assertRaises(KeyError):
            list4 = resultsHandler.json2list(json1, schema=schema)

    def test_list2json(self):
        list1 = ['Slawomir', 'Tulski', '26', 'Programmer']
        schema1 = ['first_name','last_name','age', 'occupation']
        json1 = resultsHandler.list2json(list1, schema1)
        assert(len(list(json1.keys())) == 4)
        assert(json1['age'] == '26')
        assert(json1['first_name'] == 'Slawomir')

        schema2 = ['first_name', 'last_name']
        with self.assertRaises(KeyError):
            json2 = resultsHandler.list2json(list1, schema2)

        list3 = ['Jaś', [1,2]]
        schema3 = ('name', 'grades')
        json3 = resultsHandler.list2json(list3, schema3)
        assert(json3['grades'] == [1,2])

    def test_saveResultsAsJSON(self): # listOfResults, fullpath, mode='ab+', schema=None

        # single result in listOfResults is JSON
        listOfResults = [{'last_name':'Tulski','age':'26','first_name':'Slawomir', 'occupation':'Programmer'},
                         {'last_name':'Nowak','age':'62','first_name':'Jan', 'occupation':'Cieć'},
                         {'last_name':'激し','age':'一つ目','first_name':'激しさ', 'occupation':'とこの激'}]
        
        fullpath = os.path.join(os.path.dirname(__file__), 'jsonResult1.json')
        resultsHandler.saveResultsAsJSON(listOfResults, fullpath, mode='wb')

        with open('jsonResult1.json', 'r') as outF:
            results = [eval(line) for line in outF.readlines()]
            assert(results[0]['first_name'] == 'Slawomir')
            assert(results[1]['occupation'] == 'Cieć')
            assert(results[2]['occupation'] == 'とこの激')
            assert(len(results) == 3)

        os.remove('jsonResult1.json')

        # single result in listOfResults is list
        listOfResults = [['Slawomir', 'Tulski', '26', 'Programmer'],
                         ['Jan', 'Nowak', '62', 'Manager'],
                         ['激しさ', '激し', '一つ目', 'とこの激']]
        
        fullpath = os.path.join(os.path.dirname(__file__), 'jsonResult2.json')

        with self.assertRaises(TypeError):
            resultsHandler.saveResultsAsJSON(listOfResults, fullpath, mode='wb')

        schema = ['first_name','last_name','age', 'occupation']
        resultsHandler.saveResultsAsJSON(listOfResults, fullpath, mode='wb' ,schema = schema)

        with open('jsonResult2.json', 'rb') as outF:
            results = [eval(line) for line in outF.readlines()]
            assert(results[0]['first_name'] == 'Slawomir')
            assert(results[1]['occupation'] == 'Manager')
            assert(results[2]['occupation'] == 'とこの激')
            assert(len(results) == 3)

        os.remove('jsonResult2.json')

    def test_saveResultsAsCSV(self):

        # single result in listOfResults is JSON
        listOfResults = [{'name':'event1','date':'1/1/1990','price':{'amount':10, 'currency':'USD'},'place':'Ohio'},
                         {'name':'event2','date':'1/2/1990','price':{'amount':20, 'currency':'USD'},'place':'Alabama'},
                         {'name':'event3','date':'1/3/1990','price':{'amount':30, 'currency':'USD'},'place':'Indianapolis'},
                         {'name':'event3','date':'1/4/1990','price':{'amount':40, 'currency':'USD'},'place':'Plano'}]

        fullpath = os.path.join(os.path.dirname(__file__), 'csvResult1.csv')
        resultsHandler.saveResultsAsCSV(listOfResults, fullpath, mode='wb')
        with open('csvResult1.csv', 'r') as outF:
            reader = csv.reader(outF)
            results = [row for row in csv.reader(outF)]
            # schema was not specified so order of columns is random (as output of dict.keys())
            assert(results[2][0] == 'event2' or results[2][0] == '1/2/1990' or results[2][0] == str({'amount':20, 'currency':'USD'}) or results[2][0] == 'Alabama')
        os.remove('csvResult1.csv')

        # here order of columns should correspond to schema
        schema = ('name', 'date', 'price', 'place')
        fullpath = os.path.join(os.path.dirname(__file__), 'csvResult2.csv')
        resultsHandler.saveResultsAsCSV(listOfResults, fullpath, mode='w', schema=schema)
        with open('csvResult2.csv', 'r') as outF:
            reader = csv.reader(outF)
            results = [row for row in csv.reader(outF)]
            assert(results[0][0] == 'name')
            assert(results[1][0] == 'event1')
            assert(results[1][1] == '1/1/1990')
            assert(results[2][2] == str({'amount':20, 'currency':'USD'}))
            assert(results[2][3] == 'Alabama')
            assert(results[3][0] == 'event3')
            assert(results[3][1] == '1/3/1990')
            assert(results[4][2] == str({'amount':40, 'currency':'USD'}))
            assert(results[4][3] == 'Plano')
            assert(len(results) == 5)
        os.remove('csvResult2.csv')


        # single result in listOfResults is list # 2 testy. schema i bez. i wsystko w utf8ach
        listOfResults = [['جزيرة', 'العربية', 'رف بـ شبه القارة'],
                         ['މަވެސް މިއީ',  'ބިމުގެ ގޮތު', 'ން']]
        fullpath = os.path.join(os.path.dirname(__file__), 'csvResult3.csv')
        schema = ('جزيرة','??','???')
        resultsHandler.saveResultsAsCSV(listOfResults, fullpath, mode='w', schema=schema)

        with open('csvResult3.csv', 'r') as outF:
        	reader = csv.reader(outF)
        	results = [row for row in csv.reader(outF)]
        	assert(results[0][0] == 'جزيرة')
        	assert(results[0][2] == '???')
        	assert(results[1][1] == 'العربية')
        	assert(results[2][2] == 'ން')
        	assert(len(results) == 3)
        os.remove('csvResult3.csv')


        


if __name__ == '__main__':
    unittest.main()