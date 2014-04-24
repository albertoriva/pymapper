import string
import httplib
import hits

### Globals

mapperHostname = "genome.ufl.edu"
mapperUrl = "/mapper/db-rpc"
toolName = "pymapper-1.0"

### Utils

def splitFirstLine(data):
    # Extracts the first line from `data' and returns a 
    # tuple: (firstline, rest)
    eol = string.find(data, "\n")
    return (data[0:eol], data[eol+1:])

def sendMapperRequest(request):
    # Sends `request' to the MAPPER server.
    # Returns the body of the response as a string.
    conn = httplib.HTTPConnection(mapperHostname)
    conn.request("GET", request)
    response = conn.getresponse()
    conn.close()
    return response.read()
    
def saveMapperResponse(data, filename):
    # Save `data' returned by a mapper rpc-call to `filename'
    with open(filename, "w") as f:
        f.write(data)

### Client class

class MapperDbClient():
    # Request optional parameters
    score  = False
    perc   = False
    evalue = False
    pbases = False
    pstart = False
    org    = False
    sort   = False
    # Internal
    Debug  = False

### Base methods

    def makeParamsUrl(self):
        url = "&tool=" + toolName
        if self.score:
            url = url + "&score=" + str(self.score)
        if self.perc:
            url = url + "&perc=" + str(self.perc)
        if self.evalue:
            url = url + "&eval=" + str(self.evalue)
        if self.pbases:
            url = url + "&pbases=" + str(self.pbases)
        if self.pstart:
            url = url + "&pstart=" + str(self.pstart)
        if self.org:
            url = url + "&org=" + self.org
        if self.sort:
            url = url + "&sort=" + self.sort
        return url

    def parseMapperResponse(self, data):
        # Parse a MAPPER response `data'. Extract the first line, convert
        # it to int, and signal an error if it is negative. Otherwise
        # returns the tuple (n, body) where n is the value of the first line.
        (n, body) = splitFirstLine(data)
        n = int(n)
        if n < 0:
            (errmsg, rest) = splitFirstLine(body)
            print("Error: {}".format(errmsg))
            return False
        else:
            if self.Debug:
                print("{} records returned.".format(n))
            return (n, body)

    def getMapperList(self, prefix="*"):
        request = mapperUrl + "?list=" + prefix
        if self.Debug:
            print("Submitting request: " + request)
        return sendMapperRequest(request)

    def getMapperHits(self, gene, models):
        request = mapperUrl + "?gene=" + gene + "&models=" + models + self.makeParamsUrl()
        if self.Debug:
            print("Submitting request: " + request)
        return sendMapperRequest(request)

    # Top-level methods

    def modelsToFile(self, filename, prefix="*", debug=False):
        if debug:
            self.Debug = debug
        (n, body) = self.parseMapperResponse(self.getMapperList(prefix))
        if self.Debug:
            print("Saving models to file {}".format(filename))
        saveMapperResponse(body, filename)
        return n

    def hitsToFile(self, filename, gene, models, debug=False):
        if debug:
            self.Debug = debug
        (n, body) = self.parseMapperResponse(self.getMapperHits(gene, models))
        if self.Debug:
            print("Saving hits to file {}".format(filename))
        saveMapperResponse(body, filename)
        return n

    def hitsToHitset(self, gene, models, debug=False):
        if debug:
            self.Debug = debug
        (n, body) = self.parseMapperResponse(self.getMapperHits(gene, models))
        hitset = hits.Hitset()
        hitset.initHitsetFromCsv(n, body)
        return hitset

