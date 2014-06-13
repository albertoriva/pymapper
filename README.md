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
>>> DB=pymapper.MapperDbClient() # Create the client object
>>> DB.prepare(genes="APOE,TLR1", models="M,J", filename="hits.csv") # Initialize it
>>> DB.hitsToFile() # Run query
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
