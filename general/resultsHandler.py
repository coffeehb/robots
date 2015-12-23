# built-in
import csv
import json
import os

def json2list(json, schema=None):
    """ Converts json to list. If schema is given list order is preserved. Else (default) it is random """
    if schema:
        try:
            result = [json[field] for field in schema]
            return result
        except KeyError as e:
            raise KeyError('Defined schema doesn\'t match. There is no field:{0} in results'.format(e))
    else:
        return [json[field] for field in list(json.keys())]

def list2json(list_, schema):
    """ Converts list to json (dictionary). """
    
    if len(list_) != len(schema):
        raise KeyError('Schema doesn\'t match to list. Arguments are not the same size')
    else:
        return dict(zip(schema, list_)) 

def saveResultsAsJSON(listOfResults, fullpath, mode='ab+', schema=None):
    """ 
        Saves *listOfResults* to file. *fullpath* (along with file name) and mode are required (default is ab+).
        It uses built-in open() function. Also, if single result in listOfResults is a list, schema (names of fields) 
        is required. If single result is json and schema is provided it will be omitted.
    """
    with open(fullpath, mode) as outF:
        for result in listOfResults:
            if isinstance(result, list) and not schema:
                raise TypeError('Results type is list, but schema is not provided. Cannot convert to json')
            elif isinstance(result, list) and schema:
                resultAsJson = list2json(result, schema)
                outF.write(json.dumps(resultAsJson, outF, ensure_ascii=False).encode('utf8'))
                outF.write('\n'.encode('utf8'))
            elif isinstance(result, dict):
                outF.write(json.dumps(result, outF, ensure_ascii=False).encode('utf8'))
                outF.write('\n'.encode('utf8'))

def saveResultsAsCSV(listOfResults, fullpath, mode='a+', schema=None):
    """
        Saves *listOfResults* to file. *fullpath* (along with file name) and mode are required (default is ab+).
        It uses built-in open() function. If schema is provided it will be written in first row of csv file.
    """

    # remove 'b' to avoid Python3 "TypeError: 'str' does not support the buffer interface" with binary mode and built-in csv module
    if 'b' in mode:
        mode = mode.replace('b', '')

    with open(fullpath, mode) as outF:
        writer = csv.writer(outF)
        if schema and os.stat(fullpath).st_size == 0:
            writer.writerow(schema)
        elif schema == None and isinstance(listOfResults[0], dict) and os.stat(fullpath).st_size == 0:
            schema = list(listOfResults[0].keys())
            writer.writerow(schema)

        for result in listOfResults:
            if isinstance(result, list):
                writer.writerow(result)
            elif isinstance(result, dict):
                resultAsList = json2list(result, schema=schema)
                writer.writerow(resultAsList)


"""

TODO:
- 

Features nice to have here:
- deduplication
- filter result by key column (remove empty results or with not valid values)

"""


