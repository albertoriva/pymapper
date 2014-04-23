import string
import httplib

mapperHostname = "genome.ufl.edu"
mapperUrl = "/mapper/db-rpc"
toolName = "pymapper-1.0"
pymapperDebug = False

class MapperParams():
    score  = False
    perc   = False
    evalue = False
    pbases = False
    pstart = False
    org    = False
    sort   = False

### Utils

def splitFirstLine(data):
    # Extracts the first line from `data' and returns a 
    # tuple: (firstline, rest)
    eol = string.find(data, "\n")
    return (data[0:eol], data[eol+1:])

### Base methods

def sendMapperRequest(request):
    conn = httplib.HTTPConnection(mapperHostname)
    conn.request("GET", request)
    response = conn.getresponse()
    conn.close()
    return response.read()
    
def parseMapperResponse(data):
    (n, body) = splitFirstLine(data)
    n = int(n)
    if n < 0:
        (errmsg, rest) = splitFirstLine(body)
        print("Error: {}".format(errmsg))
        return False
    else:
        if pymapperDebug:
            print("{} records returned.".format(n))
        return (n, body)

def saveMapperRequest(data, filename):
    # Save `data' returned by a mapper rpc-call to `filename'
    # stripping the 
    (n, body) = parseMapperResponse(data)
    with open(filename, "w") as f:
        f.write(body)

def getMapperList(prefix="*"):
    request = mapperUrl + "?list=" + prefix
    if pymapperDebug:
        print("Submitting request: " + request)
    return sendMapperRequest(request)

def sendMapperHits(gene, models):
    request = mapperUrl + "?gene=" + gene + "&models=" + models
    if pymapperDebug:
        print("Submitting request: " + request)
    return sendMapperRequest(request)

