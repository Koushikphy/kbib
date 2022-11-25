import os
import re
import sys
import bibtexparser
import requests_cache
from urllib.parse import quote
from rich.progress import (
    Progress,
    TextColumn,
    SpinnerColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    BarColumn,
    MofNCompleteColumn
)
from datetime import timedelta
from argparse import ArgumentParser, RawTextHelpFormatter
from rich.console import Console

try:
    import pdf2doi
    PDF_AVAILABLE = True
    pdf2doi.config.set('verbose',False)
except ImportError:
    PDF_AVAILABLE = False



class CustomParser(ArgumentParser):

    def error(self, message):
        cs = Console(stderr=True)
        cs.print(f"Error: {message}",style="red")
        self.print_help()
        sys.exit(2)



BARE_API = "http://api.crossref.org/"   # API to get bibtex information 
ABVR_API = "https://abbreviso.toolforge.org/abbreviso/a/"  # API to get abbreviated journal name

progress = Progress(
    TextColumn("[progress.description]{task.description}"),
    SpinnerColumn(),
    TimeElapsedColumn(),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    " ETA:",
    TimeRemainingColumn(),
)


session = requests_cache.CachedSession('doi_cache', 
    use_cache_dir=True,                # Save files in the default user cache dir
    cache_control=True,                # Use Cache-Control response headers for expiration, if available
    expire_after=timedelta(days=30),    # Otherwise expire responses after one day
    allowable_codes=[200, 400], 
)







def get_bib(doi):
    # Get bibtex information from Crossref APi
    url = "{}works/{}/transform/application/x-bibtex".format(BARE_API, doi)
    r = session.get(url)
    # r =requests.get(doi, headers={'Accept':'application/x-bibtex'})
    found = r.status_code == 200 
    bib = str(r.content, "utf-8")
    return found, bib


def get_all_ref(doi):
    # Get list of references from Crossref API
    url = "{}works/{}".format(BARE_API, doi)
    r = session.get(url)
    found = r.status_code == 200
    item = r.json()
    # item["message"]["short-container-title"] #abbreviated journal name
    return found, item["message"]["reference"]


def get_j_abbreviation(journal):
    # Get abbreviated journal name
    res = session.get(ABVR_API+quote(journal))
    if res.status_code ==200:
        return res.text
    else:
        print("Unable to find abbreviated journal name for "+journal)
        return journal




def shortenJrn(txt):
    # Short journal name to use as key or file name
    # short journal name is made by taking first letter of each word
    txt = txt.replace('.','')
    xt = [w[0] for w in txt.split()]
    return ''.join(xt)


rx = re.compile(r'\W+')
def get_first_author_title(txt):
    # get last name of the first author to use as key or file name
    # may remove non-english character
    fst = txt.split(' and ')[0]
    tc= fst.strip().split(' ')[-1]
    return rx.sub('',tc)



def manage(inp):
    # configure bibtex information parsed from the Crossref API
    jrnl = get_j_abbreviation(inp['journal']) 
    ath = get_first_author_title(inp['author'])
    vol = inp['volume']
    year = inp['year']
    s_jrnl = shortenJrn(jrnl)

    inp['journal'] = jrnl
    # bibtex entry key as <Short Journal name>_<Vol>_<Year>_<Last name of first author>
    # modify this to use your own style of key
    inp["ID"] = f"{s_jrnl}_{vol}_{year}_{ath}"
    return inp
    


def reconfigureBibs(bibs):
    # manage and configure all bibtex entries 
    bib_db = bibtexparser.loads(bibs)
    bib_res = [manage(elem) for elem in bib_db.entries]
    bib_db.entries = bib_res
    return bibtexparser.dumps(bib_db)
    



def getFullRefList(doi):
    # Get bibtex information for all the references
    found, tRefs = get_all_ref(doi)
    if found:
        refDOIs = [ref for ref in tRefs if "DOI" in ref]
        refNotFound = len(tRefs) - len(refDOIs)
        if refNotFound:
            print("DOIs not found for {} reference(s).".format(refNotFound))
        fullRef = []
        # for ref in tqdm(refDOIs,desc='Parsing bibtex entries from reference list'):
        with progress:
            for ref in progress.track(refDOIs,description='[green bold]Parsing bibtex entries from reference list...'):
    
                f, refVal = get_bib(ref['DOI'])
                if f:
                    fullRef.append(refVal)
        return reconfigureBibs('\n\n\n'.join(fullRef))
    else:
        raise Exception("Unable to parse reference list.")
    




def checkPdf(files):
    # check input pdf files 
    assert PDF_AVAILABLE, '''Feature not available. Install the optional feature with `pip install kbib["pdf"]`'''
    for file in files:
        assert file.endswith('.pdf'), f"{file} is not a pdf."
        assert os.path.exists(file), f"{file} not found." 


def getbibfrompdf(file):
    doi = pdf2doi.pdf2doi(file)['identifier']
    return get_bib(doi)


def pdftobib(pdfs):
    # bibtex information from pdf files
    checkPdf(pdfs)
    fullRef = []
    with progress:
        for pdf in progress.track(pdfs,description='[green bold]Parsing files for bibtex...'):
            f,bib = getbibfrompdf(pdf)
            if f:
                fullRef.append(bib)
    bibs = '\n\n'.join(fullRef)
    return reconfigureBibs(bibs)


def renamePDF(files):
    # rename pdf files with bibtex information
    checkPdf(files)
    info = []
    with progress:
        for file in progress.track(files,description='[green bold]Parsing files for info...'):
            f,bib = getbibfrompdf(file)
            if f:
                bibd = bibtexparser.loads(bib)
                bibf = manage(bibd.entries[0])
                newName = bibf['ID']+".pdf"
                info.append([file,newName])
            else:
                info.append(None)
    noInfo = sum(i is None for i in info)
    if noInfo:
        print(f"Unable to find information for {noInfo} files." )

    for nm in info:
        if nm:
            file, newName = nm
            ch = input(f"Rename {file} -> {newName}? [y/n] ")
            if ch=='y':
                os.rename(file,newName)




# def cleanDOI(doi):
#     if 'https://doi.org/' not in doi:
#         doi = 'https://doi.org/{}'.format(doi)
#     return doi



# def removeDupEntries(bibs):
#     bib_dat_DB = bibtexparser.loads(bibs)
#     bib_dat = bib_dat_DB.entries
#     idList = [i["ID"] for i in bib_dat]

#     uList = set([])

#     for i,key in enumerate(idList):
#         if key in uList:
#             index = 1
#             while True:
#                 newKey = key + "_" + str(index)
#                 if newKey not in uList:
#                     bib_dat[i]['ID'] = newKey
#                     uList.add(newKey)
#                     break
#                 else:
#                     index +=1
#             pass 
#         uList.add(key)


#     bib_dat_DB.entries = bib_dat
#     return bibtexparser.dumps(bib_dat_DB) 



# import grequests  # import it to the top
# class ProgressSession():
#     def __init__(self, urls):
#         self.progress = Progress()
#         self.task = self.progress.add_task("[green]Processing...", total=len(urls))
#         self.urls = urls
#         self.progress.start()
#     def update(self, r, *args, **kwargs):
#         if not r.is_redirect:
#             self.progress.advance(self.task)
#     def __enter__(self):
#         sess = grequests.Session()
#         sess.hooks['response'].append(self.update)
#         return sess
#     def __exit__(self, *args):
#         self.progress.stop()



# for i in range(n)
#     tmpL = ll[i*10:(i+1)*1]
#     gres = grequests.map((grequests.get(i) for i in tmpL))
#     for i in gres:
#         print(i.status_code)



# def get_urls_async(urls):
#     res = []
#     with ProgressSession(urls) as sess:
#         for i in range(13):
#             tmpL = ll[i*10:(i+1)*10]
#             # print(tmpL)
#             gres = grequests.map((grequests.get(url, session=sess, timeout = 5) for url in tmpL))
#             res.extend(gres)
#         return res
# get_urls_async(ll)
