import sys
import argparse
import bibtexparser
import pkg_resources
import requests_cache
from rich.progress import track
from datetime import timedelta
# import urllib,json

BARE_URL = "http://api.crossref.org/"

__all__ = []
version = '0.1.0'
version= pkg_resources.require('kbib')[0].version



session = requests_cache.CachedSession('doi_cache', 
    use_cache_dir=True,                # Save files in the default user cache dir
    cache_control=True,                # Use Cache-Control response headers for expiration, if available
    expire_after=timedelta(days=30),    # Otherwise expire responses after one day
    allowable_codes=[200, 400], 
)


def get_bib(doi):
    # handle situation when not successful
    url = "{}works/{}/transform/application/x-bibtex".format(BARE_URL, doi)
    r = session.get(url)
    # r =requests.get(doi, headers={'Accept':'application/x-bibtex'})
    found = r.status_code != 200 
    bib = str(r.content, "utf-8")
    return found, bib


def get_all_ref(doi):
    url = "{}works/{}".format(BARE_URL, doi)
    r = session.get(url)
    found = r.status_code == 200
    item = r.json()
    # item["message"]["short-container-title"] #abbreviated journal name
    return found, item["message"]["reference"]


def getFullRefList(doi):
    found, tRefs = get_all_ref(doi)
    if found:
        refDOIs = [ref for ref in tRefs if "DOI" in ref]
        refNotFound = len(tRefs) - len(refDOIs)
        if refNotFound:
            print("DOIs not found for {} references.".format(refNotFound))
        fullRef = []
        # for ref in tqdm(refDOIs,desc='Parsing bibtex entries from reference list'):
        for ref in track(refDOIs,description='[green bold]Parsing bibtex entries from reference list...'):
 
            f, refVal = get_bib(ref['DOI'])
            if f:
                fullRef.append(refVal)
        return '\n\n\n'.join(fullRef)
    else:
        raise Exception("Unable to parse reference list.")
    


def removeDupEntries(bibs):
    bib_dat_DB = bibtexparser.loads(bibs)
    bib_dat = bib_dat_DB.entries
    idList = [i["ID"] for i in bib_dat]

    uList = set([])

    for i,key in enumerate(idList):
        if key in uList:
            index = 1
            while True:
                newKey = key + "_" + str(index)
                if newKey not in uList:
                    bib_dat[i]['ID'] = newKey
                    uList.add(newKey)
                    break
                else:
                    index +=1
            pass 
        uList.add(key)


    bib_dat_DB.entries = bib_dat
    return bibtexparser.dumps(bib_dat_DB) 



class CustomParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('\033[91mError: %s\n\033[0m' % message)
        self.print_help()
        sys.exit(2)


def createParser():
    #main parser
    parser = CustomParser(prog="kbib",
                          formatter_class=argparse.RawTextHelpFormatter,
                          description="A tool to get bibtex entries from DOIs or PDFs",
                          epilog="Version: {}\nhttps://github.com/Koushikphy/kbib\nCreated by Koushik Naskar (koushik.naskar9@gmail.com)".format(version)
                          )

    #adding options for numerical jobs
    parser.add_argument('-bib', type=str, help="DOI to get bib entry", metavar="DOI")
    parser.add_argument('-ref', type=str, help="DOI to get bib entries for all the references", metavar="DOI")
    parser.add_argument('-pdf', type=str, help="PDF file name(s) to get DOI", metavar="PDF", nargs='*')
    parser.add_argument('-o', type=str, help="Output bib file", metavar="DOI")

    return parser


def cleanDOI(doi):
    if 'https://doi.org/' not in doi:
        doi = 'https://doi.org/{}'.format(doi)
    return doi


def writeBib(bibs, out):
    # write the bibtex information in file or stdout
    if out:
        with open(out,'w') as f:
            f.write(bibs)
    else:
        print(bibs)


def CommandsGiven(args):
    # check if any commands are given
    for elem in ['bib','ref','pdf']:
        if getattr(args,elem):
            return True
    return False


def main():
    parser = createParser()
    args = parser.parse_args()

    if not CommandsGiven(args):
        parser.print_help()
    
    if args.bib:
        f,bib = get_bib(args.bib)
        if f:
            writeBib(bib,args.o)
        else:
            print("Unable to parse bibtex information.")
    if args.ref:
        try:
            bib = getFullRefList(args.ref)
            bib = removeDupEntries(bib)
            writeBib(bib,args.o)
        except:
            print("Unable to parse bibtex information.")

    if args.pdf:
        # print(args.pdf)
        try:
            import pdf2doi
            pdf2doi.config.set('verbose',False)
            # print(args.pdf)
            def getbibfrompdf(file):
                doi = pdf2doi.pdf2doi(file)['identifier']
                f,bib = get_bib(doi)
                return f,bib

            pdfs = args.pdf
            if len(pdfs)==1:
                writeBib(getbibfrompdf(pdfs[0]),args.o)
            else:
                fullRef = []
                for pdf in track(pdfs,description='Parsing bibtex entries from reference list'):
                    f,bib = getbibfrompdf(pdf)
                    if f:
                        fullRef.append(bib)
                writeBib(removeDupEntries('\n\n\n'.join(fullRef)),args.o)
                
        except ImportError:
            print('''Feature not available. Install the optional feature with `pip install kbib["pdf"]`''')

        except:
            print("Unable to parse bibtex information.")



if __name__ == "__main__":
    main()

