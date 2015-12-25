# built-in
import os
import json
import urllib

# custom
from robots.general import requestsHandler
from robots.general import resultsHandler

class ConnectorObj():
    """
        Import.io connector object. See http://api.docs.import.io/ for more details.
    """

    def __init__(self, connectorGuid, auth):
        """
            *connectorGuid*: connector guid
            *auth*: (userID, apiKey)
        """
        self.guid = connectorGuid

        userID = auth[0]
        apiKey = urllib.parse.quote(auth[1], safe='~()*!.\'')

        self.auth = (userID, apiKey)
        self.getConnector(connectorGuid)
        self.schema = self.getConnectorSchema()

    def getConnector(self, connectorGuid):
        """
            Assign basic attributes of connector. It uses "Get Connector"
            method. Check import.io API documentation for more details.
        """
        
        url = 'https://api.import.io/store/connector/{0}?_user={1}&_apikey={2}'.format(connectorGuid, self.auth[0], self.auth[1])
        r = requestsHandler.get(url)

        if r.status_code == 200:
            response = json.loads(r.text)

            # set Connector attributes from jsonResponse
            self.name = response['name']
            self.source = response['source']
            self.creatorGuid = response['_meta']['creatorGuid']
            self.latestVersionGuid = response['latestVersionGuid']
            self.lastEditorGuid = response['_meta']['lastEditorGuid']
            self.ownerGuid = response['_meta']['ownerGuid']
            self.type = response['type']
            self.publishRequest = response['publishRequest']
            self.publishRequestGuid = response['publishRequestGuid']
            self.publishSnapshot = response['publishSnapshot']

            self.status = 'OK'

        else:
            print('Something went wrong. Couldn\'t get connector:{0}. Response status code: {1}'.format(connectorGuid, r.status_code))
            self.status = 'Failed to get ConnectorObj'

    def getConnectorSchema(self):

        """
            Returns connector schema (fields names). It uses uses "Get ConnectorVersion Schema" method. Check import.io
            API documentation for more detailsself.
        """

        if self.status == 'OK':

            url = 'https://api.import.io/store/connectorversion/{0}/schema?_user={1}&_apikey={2}'.format(self.latestVersionGuid, self.auth[0], self.auth[1])
            r = requestsHandler.get(url)

            if r.status_code == 200:
                response = json.loads(r.text)
                schema = [item['name'] for item in response['outputProperties']]
                return schema
            else:
                print('Something went wrong. Couldn\'t get schema for connector:{0}. Response status code: {1}'.format(connectorGuid, r.status_code))


    def getPublishSnapshot(self):

        """
            Publish snapshot for given connector and source. Check import.io API documentation for more details.
        """

        if self.status == 'OK':
            url = 'https://api.import.io/store/connector/{0}/_attachment/publishSnapshot/{1}?_user={2}&_apikey={3}'.format(self.guid, self.publishSnapshot, self.auth[0], self.auth[1])

            r = requestsHandler.get(url)

            if r.status_code == 200:
                response = json.loads(r.text)
                json.dumps(response, indent=4)
                print('{0}\nSnapshot published!'.format(response))
            else:
                print('Something went wrong. Couldn\'t publish snapshot for connector:{0}. Response status: {1}'.format(self.connectorGuid, r.status_code))

    def saveResults(self, results, fullpath=None, outputFormat='json', mode='ab+', schema=None):

        """
            Saves *results* (list of results from query) to file. *outputFormat* can be csv or json (json by default).
        """
       
        if outputFormat == 'json':
            resultsHandler.saveResultsAsJSON(results, fullpath, mode=mode, schema=schema)
        elif outputFormat == 'csv':
            requestsHandler.saveResultsAsCSV(results, fullpath, mode=mode, schema=schema)
        

class Extractor(ConnectorObj):

    def __init__(self, connectorGuid, auth):
        ConnectorObj.__init__(self, connectorGuid, auth)

    def query(self, sourcen, headers = 'random', proxies=None):
        """ Querying Extractor with given URL. Returns list of results, where each result is dictionary (json) """

        if self.status == 'OK':
            url = 'https://api.import.io/store/data/{0}/_query?input/webpage/url={1}&_user={2}&_apikey={3}'.format(self.guid, urllib.parse.quote(source), self.auth[0], self.auth[1])

            r = requestsHandler.get(url, headers = 'random', proxies=None)
            if r.status_code == 200:
                response = json.loads(r.text)

                return response['results']



if __name__ == '__main__':

    # some simple tests

    # auth = () put here your user guid and api key

    # guid = "bcfbcf84-cce9-494f-ae8b-6132579c04f2" # allegro listing connector
    guid = "e24d674e-580f-4f5a-92d7-b083354bfd30" # allegro item extracotr
    

    extractor = Extractor(guid, auth)
    extractor.getPublishSnapshot()

    sources = ['http://allegro.pl/okazja-mega-cena-laptop-hp-250g-15-4-kamera-xp-i5522903978.html',
               'http://allegro.pl/4-rdzenie-acer-aspire-e-4x2-16-500gb-4gb-win8-hdmi-i5036735094.html',
               'http://allegro.pl/laptop-lenovo-gamer-i5-8gb-1tb-radeon-r5-230m-i5221219416.html',
               'http://allegro.pl/sony-vaio-multi-flip-14-svf14-i5-8gb-1tb-ssd-2w1-i5720374281.html']

    for src in sources:
        print(extractor.query(src)[0]['title'])


"""

TODO:

- implement Connector class
    Methods:
    + quering -> https://api.import.io/store/data/bcfbcf84-cce9-494f-ae8b-6132579c04f2/_query?input/item=laptop&_user=c80a8940-d8e6-493b-8f16-8d657709a3c3&_apikey=c80a8940d8e6493b8f168d657709a3c315e56fba30587c32631fd593048df7260125674e969e9fb9e89e463ec8041f6f86862f618c4ea98c59d2bcdc73e952837fa510bab6b507e984c9d7cc3f124dec

"""