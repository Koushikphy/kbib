import requests, urllib,json,bibtexparser,sys,argparse,pkg_resources
from tqdm import tqdm

BARE_URL = "http://api.crossref.org/"




def get_bib(doi):
    # handle situation when not successful
    url = "{}works/{}/transform/application/x-bibtex".format(BARE_URL, doi)
    r = requests.get(url)
    # r =requests.get(doi, headers={'Accept':'application/x-bibtex'})
    found = r.status_code != 200 
    bib = str(r.content, "utf-8")
    return found, bib


def get_all_ref(doi):
    url = "{}works/{}".format(BARE_URL, doi)
    r = requests.get(url)
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
        # print("Parsing bibtex entries for reference list. Please wait...")
        fullRef = []
        for ref in tqdm(refDOIs,desc='Parsing bibtex entries for reference list'):
 
            f, refVal = get_bib(ref['DOI'])
 
            fullRef.append(refVal)
        return '\n\n\n'.join(fullRef)




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




doi = 'https://doi.org/10.1021/acs.jpca.2c01209'






version = '0.1.0'
__all__ = []
# version= pkg_resources.require('kbib')[0].version

class CustomParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('\033[91mError: %s\n\033[0m' % message)
        self.print_help()
        sys.exit(2)


def listOfInts(val):
    try:
        val = int(val)
        if val < 0:
            raise ValueError
    except:
        raise argparse.ArgumentTypeError("Only list of positive are allowed")
    return val


def createParser():
    #main parser
    parser = CustomParser(prog="kbib",
                          formatter_class=argparse.RawTextHelpFormatter,
                          description="Get all bibtex entries from DOI",
                          epilog="Version: {}\nhttps://github.com/Koushikphy/kbib\nCreated by Koushik Naskar (koushik.naskar9@gmail.com)".format(version)
                          )

    #adding options for numerical jobs
    parser.add_argument('-bib', type=str, help="Provide DOI to get bib entry", metavar="DOI")
    parser.add_argument('-ref', type=str, help="Provide DOI to get bib entries for all the references ", metavar="DOI")
    parser.add_argument('-o', type=str, help="Output bib file", metavar="DOI")

    return parser.parse_args()


def cleanDOI(doi):
    pass


def writeBib(bibs, out):
    if out:
        with open(out,'w') as f:
            f.write(bibs)
    else:
        print(bibs)


def main():
    args = createParser()
    
    if args.bib:
        f,bib = get_bib(args.bib)
        writeBib(bib,args.o)
    if args.ref:
        bib = getFullRefList(args.ref)
        bib = removeDupEntries(bib)
        writeBib(bib,args.o)






if __name__ == "__main__":
    main()

