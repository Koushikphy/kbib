## `kbib`: Get all bibtex entries from DOIs or PDFs.
[![Alt text](https://img.shields.io/pypi/v/kbib.svg?logo=pypi)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/pyversions/kbib.svg?logo=python)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/dm/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/l/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/status/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://github.com/koushikphy/kbib/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Koushikphy/kbib/releases/latest)

### ⚒ Instalation
Download and install the latest package from the [release section](https://github.com/Koushikphy/kbib/releases/latest) or directly by pip
```bash
pip install kbib
```
For paring bibtex information from PDF files, optional dependencies need to be installed

```bash
pip install kbib['pdf']
```



### ⚡ Features
1. Get bibtex entry from DOI.
3. Get bibtex entry from article pdf.
2. Get full list of references of an article as bibtex entries.



### 🚀 Usage 
Use the command line tool `kbib` as 
```bash
kbib [-h] [-bib DOI] [-ref DOI] [-o DOI]
```

| Argument    |  Description|
| ----------- | ----------- 
|    `-bib`     |DOI to get bib entry  |
|    `-ref`     | DOI to get bib entries for all the references | 
|    `-pdf`     | PDF file name(s) to get DOI | 
|    `-o`      | Output bib file | 


#### Limitation:
Currently it parses DOI information from Crossref API (api.crossref.org). So if the article is not indexed in Crossref database this tool will fail to get the necessary information.


#### Work-in-Progress:
Concurrent API calls for faster parsing of bibtex information.