## `kbib`: A tool to get bibtex entries from DOIs or PDFs.
[![Alt text](https://img.shields.io/pypi/v/kbib.svg?logo=pypi)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/pyversions/kbib.svg?logo=python)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/dm/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/l/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/status/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://github.com/koushikphy/kbib/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Koushikphy/kbib/releases/latest)

### 🐱‍🏍 Installation
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
kbib [-h] [-bib DOI] [-ref DOI] [-pdf [PDF [PDF ...]]] [-o DOI]
```

| Argument    |  Description|
| ----------- | ----------- 
|    `-bib`    | DOI to get bibtex entry |
|    `-ref`    | DOI to get bibtex entries for all the references | 
|    `-pdf`    | PDF file name(s) to get DOI | 
|    `-o`      | Output bib file | 

1. Get bibtex from a DOI
    ```bash
    kbib -bib https://doi.org/10xxxxxx
    ```
1. Get bibtex from a DOI and store in a file 'ref.bib'
    ```bash
    kbib -bib https://doi.org/10xxxxxx -o ref.bib
    ```
1. Get the full reference list of an article as bibtex entries and save as ref.bib
    ```bash
    kbib -ref https://doi.org/10xxxxxx -o ref.bib
    ```
1. Get bibtex from a PDF named article.pdf
    ```bash
    kbib -pdf article.pdf
    ```
1. Get bibtex from all pdf in the current folder
    ```bash
    kbib -pdf *.pdf
    ```


#### ⚓Limitation:
Currently it parses DOI information from [Crossref API](https://github.com/CrossRef/rest-api-doc). So if the article is not indexed in Crossref database this tool will fail to get the necessary information.


#### ⚒ Work-in-Progress:
1. Concurrent API calls for faster parsing of bibtex information.
2. Set bibtex entry keys in a predefined format.
3. Ise abbreviated journal names.