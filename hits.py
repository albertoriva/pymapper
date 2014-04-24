import cStringIO

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

    def initHitsetFromCsv(self, n, data):
        self.nhits = n
        reader = cStringIO.StringIO(data)
        reader.readline()       # skip header
        for i in range(n):
            h = Hit()
            d1 = reader.readline().rstrip("\n").split("\t") #  read main line
            d2 = reader.readline().rstrip("\n").split("\t") # read line containing alignment match
            d3 = reader.readline().rstrip("\n").split("\t") # read line containing alignment sequence
            reader.readline()                             # skip empty line
            d1[14] = (d1[14], d2[14], d3[14])
            h.initHit(d1)
            self.hits.append(h)
        return self.hits
