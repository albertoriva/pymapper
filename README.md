# pymapper
========

**pymapper** is a Python interface to the MAPPER database of predicted transcription
factor binding sites, available at http://genome.ufl.edu/mapper/. pymapper uses the **db-rpc**
backdoor to send queries directly to MAPPER bypassing the web-based interface. Results
can be returned as a tab-delimited file, or as a Python object.

## Basic usage

```python
>>> import pymapper
>>> DB=pymapper.MapperDbClient()
>>> DB.genes="APOE"
```
