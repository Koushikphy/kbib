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
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import timedelta
from rich import print as rprint
try:
    import pdf2doi
    PDF_AVAILABLE = True
    pdf2doi.config.set('verbose',False)
except ImportError:
    PDF_AVAILABLE = False



class CustomParser(ArgumentParser):

    def error(self, message):
        rprint(f"[red]Error: {message}")
        self.print_help()
        sys.exit(2)



BARE_API = "http://api.crossref.org/"   # API to get bibtex information 
ABVR_API = "https://abbreviso.toolforge.org/abbreviso/a/"  # API to get abbreviated journal name
DOI_API  = 'https://doi.org/'

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

# regular expression rules
rx    = re.compile(r'\W+')
r_sub = re.compile(r'\$\\less\$sub\$\\greater\$(.*?)\$\\less\$/sub\$\\greater\$')
r_sup = re.compile(r'\$\\less\$sup\$\\greater\$(.*?)\$\\less\$/sup\$\\greater\$')
r_it  = re.compile(r'\$\\less\$i\$\\greater\$(.*?)\$\\less\$/i\$\\greater\$')
r_m   = re.compile(r'\$\\mathplus\$')
r_n   = re.compile(r'\n')



def cleanDOI(doi):
    return doi if DOI_API in doi else f'{DOI_API}/{doi}'

def cleanText(txt):
    return rx.sub('',txt)


def cleanTitle(txt):
    ss = r_sub.sub(r"$_{\1}$",txt)
    ss = r_sup.sub(r"$^{\1}$",ss)
    ss = r_it.sub(r"\\emph{\1}",ss)
    ss = r_m.sub("+",ss)
    ss = r_n.sub(" ",ss)
    return ss




def get_bib(doi):
    # Get bibtex information from Crossref APi

    # cDoi = cleanDOI(doi)
    # r = session.get(cDoi, headers={'Accept':'application/x-bibtex'})
    # returns in unicode format but slow
    # r = session.get(cDoi, headers={'Accept':'text/x-bibliography; style=bibtex'})  
    # fast but title is messed up during unicode/xml to string conversion
    r = session.get(f"{BARE_API}works/{doi}/transform/application/x-bibtex")  
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
    # Get abreviated journal name
    res = session.get(ABVR_API+quote(journal))
    if res.status_code ==200:
        return res.text
    else:
        print("Unable to find abbreviated journal name for "+journal)
        return journal



def shortenJrn(txt):
    # Short journal name to use as key or file name
    txt = txt.replace('.','')
    xt = [w[0] for w in txt.split()]
    sn =  ''.join(xt)
    return cleanText(sn)


def get_first_author_title(txt):
    # get last name of the first author to use as key or file name
    # may remove non-english character
    fst = txt.split(' and ')[0]
    tc= fst.strip().split(' ')[-1]
    return cleanText(tc)



def manage(inp):
    # configure bibtex information parsed from the Crossref API
    try:
        jrnl = get_j_abbreviation(inp['journal']) 
        ath = get_first_author_title(inp['author'])
        inp['journal'] = jrnl
        # clean the tile 
        inp["title"] = cleanTitle(inp["title"])

        vol = inp['volume']
        year = inp['year']
        s_jrnl = shortenJrn(jrnl)

        # bibtex entry key as <Short Journal name>_<Vol>_<Year>_<Last name of first author>
        # modify this to use your own style of key
        inp["ID"] = f"{s_jrnl}_{vol}_{year}_{ath}"
        # inp["ID"] = f"{ath}{year}_{s_jrnl}_{vol}" # second type
    except KeyError as e:
        print(f"Key {e} not found for doi: {inp['doi']}",file=sys.stderr)
    finally:
        return inp





def reconfigureBibs(bibs):
    # manage and configure all bibtex entries 
    bib_db = bibtexparser.loads(bibs)
    bib_res = [manage(elem) for elem in bib_db.entries]

    # check for duplicate keys
    if len(bib_res)>1:
        bibKeys = set()
        for i,r in enumerate(bib_res):
            key = r["ID"]
            if key not in bibKeys:
                bibKeys.add(r['ID'])
            else:
                try: # check if page number is available
                    kTmp = r['pages'].split('--')[0]
                except KeyError:  # if page is not there then take first 5 letter of the title
                    kTmp = cleanText(r['title'])[:5].replace(' ','')
                newKey = f"{key}_{kTmp}"
                bib_res[i]["ID"] = newKey
        
    bib_db.entries = bib_res
    return bibtexparser.dumps(bib_db)
    



def getFullRefList(doi):
    # Get bibtex information for all the references
    found, tRefs = get_all_ref(doi)
    if found:
        refDOIs, noDOIs = [], []
        for r in tRefs:
            if "DOI" in r:
                refDOIs.append(r)
            else:
                noDOIs.append(r)

        if len(noDOIs):
            rprint(f"[red]DOIs not found for following {len(noDOIs)} references:")
            for r in noDOIs:
                print(r)

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




# progress = Progress()

# progress.start()
# task = progress.add_task("Getting references-------------",total=124)

# async def get(url, session):
#     async with session.get(url=url) as response:
#         resp = await response.read()
#         progress.update(task,advance=1)
#         return resp

# async def main(urls):
#     connector = aiohttp.TCPConnector(limit=5)
#     async with aiohttp.ClientSession(trust_env=True,connector=connector) as session:
#         ret = await asyncio.gather(*[get(url, session) for url in urls])
#     print(ret)


# asyncio.run(main(dois))
# progress.stop()