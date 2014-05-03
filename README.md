# pymapper
========

## Introduction
**pymapper** is a Python interface to the MAPPER database of predicted transcription
factor binding sites, available at http://genome.ufl.edu/mapper/. pymapper uses the 
**db-rpc** backdoor to send queries directly to MAPPER bypassing the web-based interface. 
Results can be returned as a tab-delimited file, or as a Python object.

## Basic usage

```python
>>> import pymapper
>>> DB=pymapper.MapperDbClient() # Create the client object
>>> DB.genes="APOE,TLR1"         # Genes to query
>>> DB.models="M,J"              # Model libraries to use
>>> DB.filename="hits.csv"       # Set destination file
>>> DB.hitsToFile()              # Run query
```

A client object can be reused for multiple queries. Simply change the attributes
you need and re-run the query:

```python
>>> DB.models="T" # Use a different model library on the same genes
>>> DB.filename="hits2.csv" # Don't overwrite previous results
>>> DB.hitsToFile()
```
