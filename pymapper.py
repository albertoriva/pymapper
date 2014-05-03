import argparse
import string
import httplib
import cStringIO

### Globals

VERSION="1.0"

mapperHostname = "genome.ufl.edu"
mapperUrl = "/mapper/db-rpc"
toolName = "pymapper-$(VERSION)"

### Utils

def splitFirstLine(data):
    """Extracts the first line from `data' and returns a tuple: (firstline, rest)."""
    part = data.partition("\n")
    return (part[0], part[2])

def lineToList(line):
    """Converts a tab-delimited line into a list of strings, removing the terminating \n and \r."""
    return line.rstrip("\n\r").split("\t")

def sendMapperRequest(request):
    """Sends `request' to the MAPPER server. Returns the body of the response as a string."""
    conn = httplib.HTTPConnection(mapperHostname)
    conn.request("GET", request)
    response = conn.getresponse()
    conn.close()
    return response.read()
    
def saveMapperResponse(data, filename):
    """Save `data' returned by a mapper rpc-call to `filename'."""
    with open(filename, "w") as f:
        f.write(data)

### Errors from db-rpc

class MapperError(Exception):
    """Base class for errors generated by the Mapper db-rpc interface."""
    message = ""
    
    def __init__(self, msg):
        self.message = msg

class MapperBadArgsError(MapperError):
    pass

class MapperNoGeneError(MapperError):
    pass

class MapperNoModelsError(MapperError):
    pass

class MapperInternalError(MapperError):
    pass

### Class representing Mapper hits

class Hit():
    GeneID = ""
    Gene = ""
    Org = ""
    Accession = ""
    Model = ""
    Factor = ""
    Strand = ""
    Chrom = ""
    Start = 0
    End = 0
    Region = ""
    Score = 0
    Eval = 0
    Conserved = False
    Alignment_model = ""
    Alignment_match = ""
    Alignment_sequence = ""

    def initHit(self, data):
        # Fill slots of this hit using values from the list `data'
        # (obtained by parsing a MAPPER csv)
        self.GeneID = data[0]
        self.Gene = data[1]
        self.Org = data[2]
        self.Accession = data[3]
        self.Model = data[4]
        self.Factor = data[5]
        self.Strand = data[6]
        self.Chrom = data[7]
        self.Start = int(data[8])
        self.End = int(data[9])
        self.Region = data[10]
        self.Score = float(data[11])
        self.Eval = float(data[12])
        self.Conserved = data[13]
        self.Alignment = data[14]

class Hitset():
    hits = []
    nhits = 0
    header = []

    def initHitsetFromCsv(self, n, data):
        self.nhits = n
        reader = cStringIO.StringIO(data)
        header = lineToList(reader.readline()) # read and store header
        for i in range(n):
            h = Hit()
            d1 = lineToList(reader.readline()) # read main line
            d2 = lineToList(reader.readline()) # read line containing alignment match
            d3 = lineToList(reader.readline()) # read line containing alignment sequence
            reader.readline()                  # skip empty line
            d1[14] = (d1[14], d2[14], d3[14])
            h.initHit(d1)
            self.hits.append(h)
        return self.hits

    def HitsetIterator(self):
        """Returns an iterator to loop over the hits in this hitset."""
        for i in range(self.nhits):
            yield self.hits[i]

    def HitsetFactors(self):
        """Returns a list of all factors appearing in this hitset, without duplicates. 
Useful to quickly check if a TFBS for a desired factor is present in the hitset."""
        factors = {}
        for h in self.hits:
            factors[h.Factor] = True
        return sorted(factors.keys())

    def HitsetModels(self):
        """Returns a list of all models appearing in this hitset, without duplicates. 
Useful to quickly check if a TFBS from a desired model is present in the hitset."""
        models = {}
        for h in self.hits:
            models[h.Model] = True
        return sorted(models.keys())

### Client class

class MapperDbClient():
    # Main arguments
    genes    = None
    models   = None
    filename = None

    # Request optional parameters
    score    = None
    perc     = None
    evalue   = None
    pbases   = None
    pstart   = None
    org      = None
    sort     = None

    # Internal
    mode     = None
    Debug    = False

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
            if n == -2:
                raise MapperNoGeneError(errmsg)
            elif n == -3:
                raise MapperNoModelsError(errmsg)
            elif n == -4:
                raise MapperBadArgsError(errmsg)
            else:
                raise MapperInternalError(errmsg)
                
        else:
            if self.Debug:
                print("{} records returned.".format(n))
            return (n, body)

    def getMapperList(self):
        request = mapperUrl + "?list=" + self.models
        if self.Debug:
            print("Submitting request: " + request)
        return sendMapperRequest(request)

    def getMapperHits(self):
        request = mapperUrl + "?gene=" + self.genes + "&models=" + self.models + self.makeParamsUrl()
        if self.Debug:
            print("Submitting request: " + request)
        return sendMapperRequest(request)

    # Top-level methods

    def modelsToFile(self, debug=False):
        if debug:
            self.Debug = debug
        (n, body) = self.parseMapperResponse(self.getMapperList())
        if self.filename:
            if self.Debug:
                print("Saving models to file {}".format(self.filename))
            saveMapperResponse(body, self.filename)
        else:
            print(body)
        return n

    def hitsToFile(self, debug=False):
        if debug:
            self.Debug = debug
        (n, body) = self.parseMapperResponse(self.getMapperHits())
        if self.filename:
            if self.Debug:
                print("Saving hits to file {}".format(self.filename))
            saveMapperResponse(body, self.filename)
        else:
            print(body)
        return n

    def hitsToHitset(self, debug=False):
        if debug:
            self.Debug = debug
        (n, body) = self.parseMapperResponse(self.getMapperHits())
        if n:
            hitset = Hitset()
            hitset.initHitsetFromCsv(n, body)
            return hitset

# Main

def parseArgs():
    DB = MapperDbClient()
    parser = argparse.ArgumentParser(description='Query the MAPPER database.',
                                     epilog='This tool can work in two modes, query or list. In query mode, it retrieves TFBSs from the Mapper database for the gene(s) specified by the -g argument. In this case the -m argument is optional and default to all models. In list mode, invoked when -m is specified but -g is not, the tool returns the list of known models. If an optional prefix is specified after -m, it returns data for the factors whose name starts with that prefix.')
    parser.add_argument('-g', help='A comma-separated list of gene identifiers (HUGO gene names, Entrez GeneIDs, mRNA accession numbers or CG identifiers for Drosophila genes).',
                        dest='genes', metavar='genes')
    parser.add_argument('-m', help="A comma-separated list of MAPPER models. The special values `M', `T', and `J' indicate the MAPPER, TRANSFAC, and JASPAR model libraries respectively.", 
                        dest='models', metavar='models', nargs='?', const='*', default='Y')
    parser.add_argument('-f', help='The name of the file that TFBS data will be written to.', 
                        dest='filename', metavar='filename')
    parser.add_argument('-s', help='Lower threshold on the predicted TFBS score.',
                        dest='score', metavar='score', type=float)
    parser.add_argument('-p', help='Lower threshold on the percentile of TFBS score.',
                        dest='perc', metavar='perc', choices=['p50', 'p80', 'p85', 'p90', 'p95', 'p99'])
    parser.add_argument('-e', help='Upper threshold on the predicted TFBS E-value', 
                        dest='evalue', metavar='evalue', type=float)
    parser.add_argument('-pb', help='Size of the region to be scanned, upstream of the transcript start or ATG of the gene (see the -ps argument).', 
                        dest='pbases', metavar='size', type=int)
    parser.add_argument('-ps', help='Scan region upstream of the transcript start (T) or the ATG of the gene (C).', 
                        dest='pstart', metavar='start', choices=['T', 'C'])
    parser.add_argument('-o', help='Organism two-letter code.', 
                        dest='org', metavar='org', choices=['Hs', 'Mm', 'Dm'])
    parser.add_argument('-r', help='How to order the results. Possible values: M (by model number), N (by factor name), P (by position), S (by score, descending), s (by score, ascending), or E (by E-value).', 
                        dest='sort', metavar='sort', choices=['M', 'N', 'P', 'S', 's', 'E'])
    parser.add_argument('-d', help='Enable debugging mode.', 
                        action='store_true', dest='Debug')
    parser.add_argument('-v', help='Display client version number.',
                        action='version', version=VERSION)
    args = parser.parse_args(namespace=DB)

    # Determine mode
    if DB.genes == None:
        # Are we in list mode?
        if DB.models == None:
            parser.error("At least one of -g and -m are required. Use -h for full help.")
        else:
            DB.mode = 'list'
    else:
        DB.mode = 'query'
    return DB

def main(DB):
    if DB.mode == 'query':
        DB.hitsToFile(debug=DB.Debug)
    elif DB.mode == 'list':
        DB.modelsToFile(debug=DB.Debug)

if __name__ == "__main__":
    DB = parseArgs()
    main(DB)
    # DB.hitsToFile(DB.filename, DB.genes, DB.models)

