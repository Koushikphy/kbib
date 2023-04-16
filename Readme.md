## `kbib`: A command line tool to get bibtex information from DOIs and PDFs.
[![Alt text](https://img.shields.io/pypi/v/kbib.svg?logo=pypi)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/pyversions/kbib.svg?logo=python)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/dm/kbib.svg)](https://pypistats.org/packages/kbib)
[![Alt text](https://img.shields.io/pypi/l/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://img.shields.io/pypi/status/kbib.svg)](https://pypi.org/project/kbib/)
[![Alt text](https://github.com/koushikphy/kbib/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Koushikphy/kbib/releases/latest)



### ⚡ Features
1. Get bibtex information from DOI.
2. Get bibtex information from article pdf.
3. Get full list of references of an article as a .bib file.
4. Directly rename pdf files with bibtex information.
5. Find duplicate bib entries in bibtex files.

### 🛠️ Installation
Download and install the latest package from the [release section](https://github.com/Koushikphy/kbib/releases/latest) or directly by pip
```bash
pip install kbib
```
For parsing bibtex information from PDF files, optional dependencies need to be installed

```bash
pip install kbib['pdf']
```


### 🚀 Usage 
Use the command line tool `kbib` as 
```bash
kbib [-h] [-bib DOI] [-ref DOI] [-pdf [PDF [PDF ...]]] [-ren [PDF [PDF ...]]] [-dup [BIB [BIB ...]]] [-o DOI]
```

| Argument    |  Description|
| ----------- | ----------- 
|    `-bib`    | DOI to get bibtex entry |
|    `-ref`    | DOI to get bibtex entries for all the references | 
|    `-pdf`    | PDF file name(s) to get bibtex info | 
|    `-ren`    | PDF file name(s) to rename with bibtex info | 
|    `-dup`    | Bib file name(s) to find duplicates. | 
|    `-o`      | Output bib file | 

* Get bibtex from a DOI
    ```bash
    kbib -bib https://doi.org/10xxxxxx
    ```
* Get bibtex from a DOI and store in a file 'ref.bib'
    ```bash
    kbib -bib https://doi.org/10xxxxxx -o ref.bib
    ```
* Get the full reference list of an article as bibtex entries and save as ref.bib
    ```bash
    kbib -ref https://doi.org/10xxxxxx -o ref.bib
    ```
* Get bibtex from a PDF named article.pdf
    ```bash
    kbib -pdf article.pdf
    ```
* Get bibtex from all pdfs in the current folder
    ```bash
    kbib -pdf *.pdf
    ```
* Rename pdf files with bibtex information
    ```bash
    kbib -ren article.pdf
    # or
    kbib -ren *.pdf
    ```
* Find duplicate bib entries in bibtex files.
    ```bash
    kbib -dup article_1.bib article_2.bib
    ```

#### ⚓Limitation:
- `kbib` parses DOI information from [Crossref API](https://github.com/CrossRef/rest-api-doc). So if the article is not indexed in Crossref database this tool will fail to get the necessary information. Also the API may temporarily block requests from an IP if a large number of queries are made within a short period of time.
- Special/Latex characters in the title may gets messed up during the API call. One needs to be careful using title field for the bibtex created by `kbib`.
- For bibtex keys and renaming files, `kbib` uses format as `<Short Journal Name>_<Volume>_<Year>_<Last name of first author>`, which is presently hardcoded in the tool. Therefore, one can not use any desired format through the command line.


#### ⏳ Work-in-Progress:
- Concurrent/Parallel API calls for faster parsing of bibtex information.

