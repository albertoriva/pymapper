# pymapper
========

## Introduction
**pymapper** is a Python interface to the MAPPER database of predicted transcription
factor binding sites, available at http://genome.ufl.edu/mapper/. pymapper uses the 
**db-rpc** backdoor to send queries directly to MAPPER bypassing the web-based interface. 
Results can be returned as a tab-delimited file, or as a Python object.

## Basic usage

The following code shows how to create a MAPPER client object and to use it to
send a query to MAPPER.

```python
>>> import pymapper
>>> DB=pymapper.MapperDbClient()  # Create the client object
>>> DB.genes = "APOE,TLR1"        # Genes to query
>>> DB.models = "M,J"             # Model libraries to use
>>> DB.filename = "hits.csv"      # Set destination file
>>> DB.hitsToFile()               # Run query
246                               # Number of hits written to 'hits.csv'
```

Alternatively, you can use the prepare() method to initialze the client object:

```python
>>> import pymapper
>>> DB=pymapper.MapperDbClient()  # Create the client object
>>> DB.prepare(genes="APOE,TLR1", models="M,J", filename="hits.csv") # Initialize it
>>> DB.hitsToFile()               # Run query
246
```

A client object can be reused for multiple queries. Simply assign new values to the 
parameters you need to change and re-run the query:

```python
>>> DB.models = "T"           # Use a different model library on the same genes
>>> DB.filename = "hits2.csv" # Don't overwrite previous results
>>> DB.hitsToFile()
```

## Query parameters

The client object contains several attributes corresponding to query parameters that
can be modified. They are:

Parameter | Description
----------|------------
score     |  Lower threshold on the predicted TFBS score.
perc      |  Lower threshold on the percentile of TFBS score (possible values: p50, p80, p90, p95, p99).
evalue    |  Upper threshold on the predicted TFBS E-value.
pbases    |  Size of the region to be scanned, upstream of the transcript start or ATG of the gene (see pstart).
pstart    |  Scan region upstream of the transcript start (T) or the ATG of the gene (C).
org       |  Organism two-letter code (currently 'Hs', 'Mm', or 'Dm').
sort      |  How to order the results. Possible values: M (by model number), N (by factor name), P (by position), S (by score, descending), s (by score, ascending), or E (by E-value).

For example:

```python
>>> DB.score = 5.0  # find hits with score >= 5
>>> DB.sort = 'P'   # and sort them by position
>>> DB.hitsToFile() # re-run query
```

## Generating hitsets

The results of a MAPPER query can be returned as a Python object of classs Hitset.
This is accomplished using the function hitsToHitset():

```python
>>> DB.prepare(genes='APOE,TLR1', models='J')
>>> hits = DB.hitsToHitset()  # Generate hitset
>>> hits.nits
7                             # Number of hits in hitset
```

The contents of a hitset can be iterated over. For example, to print
all the scores of the hits in this hitset:

```python
>>> for h in hits.hits:
...  print h.Score
...
3.8
5.7
3.8
5.6
5.8
5.4
3.8
```

The hits attribute of a hitset is a list of Hit objects. A hit has the following attributes:

Attribute | Description
----------|------------
GeneID    | NCBI ID of this gene
Gene      | Gene symbol
Org       | Organism
Accession | mRNA accession number
Model     | Model identifier
Factor    | Transcription factor name
Strand    | Strand of hit
Chrom     | Chromosome
Start     | Start position of hit on chromosome
End       | End position of hit on chromosome
Region    | Gene region (e.g., 'Promoter')
Score     | Score of hit
Eval      | E-value of hit
Alignment | A 3-tuple containing the alignment details

The two methods HitsetFactors() and HitsetModels() return a list of all the
factors and all the models appearing in a hitset, respectively:

```python
>>> hits.HitsetFactors()
['Dr', 'hkb', 'opa', 'run::Bgb', 'tll']
>>> hits.HitsetModels()
['MA0188', 'MA0242', 'MA0450', 'MA0456', 'MA0459']
```

## Model list
A list of all models known to MAPPER can be obtained with the modelsToFile() method.
The models to be returned can be selected using the <i>models</i> attribute (use models='*'
to select all models). If <i>filename</i> is specified the models will be written
to a file, otherwise they will be printed to standard output.

```python
>>> DB.prepare(models='*', filename='models.csv')
>>> DB.modelsToFile()
6322 records returned.
Saving models to file models.csv
6322
```

## Command-line usage
**pymapper** can be used as a command-line tool. The syntax is:

```bash
pymapper.py [-h] [-g genes] [-m [models]] [-f filename] [-s score]
            [-p perc] [-e evalue] [-pb size] [-ps start] [-o org]
            [-r sort] [-d] [-v]
```

This tool can work in two modes, <i>query</i> or <i>list</i>. In query mode, it retrieves
TFBSs from the Mapper database for the gene(s) specified by the -g argument.
In this case the -m argument is optional and defaults to all models. In list
mode, invoked when -m is specified but -g is not, the tool returns the list of
known models. If an optional prefix is specified after -m, it returns data for
the factors whose name starts with that prefix.

The following table lists available command-line options with their meaning.

<table>
  <thead>
    <tr><th>Option</th><th>Description</th></tr>
  </thead>
  <tbody>
    <tr><td nowrap>-h, --help</td><td>Show this help message and exit</td></tr>
    <tr><td nowrap>-g genes</td><td>A comma-separated list of gene identifiers (HUGO gene names, Entrez GeneIDs, mRNA accession numbers or CG identifiers for Drosophila genes).</td></tr>
    <tr><td nowrap>-m [models]</td><td>A comma-separated list of MAPPER models. The special values `M`, `T`, and `J` indicate the MAPPER, TRANSFAC, and JASPAR model libraries respectively.</td></tr>
    <tr><td nowrap>-f filename</td><td>The name of the file that TFBS data will be written to.</td></tr>
    <tr><td nowrap>-s score</td><td>Lower threshold on the predicted TFBS score.</td></tr>
    <tr><td nowrap>-p perc</td><td>Lower threshold on the percentile of TFBS score.</td></tr>
    <tr><td nowrap>-e evalue</td><td>Upper threshold on the predicted TFBS E-value</td></tr>
    <tr><td nowrap>-pb size</td><td>Size of the region to be scanned, upstream of the transcript start or ATG of the gene (see the -ps argument).</td></tr>
    <tr><td nowrap>-ps start</td><td>Scan region upstream of the transcript start (`T`) or the ATG of the gene (`C`).</td></tr>
    <tr><td nowrap>-o org</td><td>Organism two-letter code.</td></tr>
    <tr><td nowrap>-r sort</td><td>How to order the results. Possible values: `M` (by model number), `N` (by factor name), `P` (by position), `S` (by score, descending), `s` (by score, ascending), or `E` (by E-value).</td></tr>
    <tr><td nowrap>-d</td><td>Enable debugging mode.</td></tr>
    <tr><td nowrap>-v</td><td>Display client version number.</td></tr>
  </tbody>
</table>

## Credits
**csvtoxls.py** is (c) 2014, A. Riva, <A href='http://dibig.biotech.ufl.edu'>DiBiG</A>, <A href='http://biotech.ufl.edu/'>ICBR Bioinformatics</A>, University of Florida
