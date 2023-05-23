import pkg_resources
from kbib.utils import (
    CustomParser,
    RawTextHelpFormatter,
    get_bib,
    reconfigureBibs,
    getFullRefList,
    pdftobib,
    renamePDF,
    listDuplicates
)


__all__ = []
# version = '0.1.1'
version= pkg_resources.require('kbib')[0].version





def createParser():
    #main parser
    parser = CustomParser(prog="kbib",
        formatter_class=RawTextHelpFormatter,
        description="A command line tool to get bibtex information from DOIs and PDFs",
        epilog="Version: {}\nhttps://github.com/Koushikphy/kbib\nCreated by Koushik Naskar (koushik.naskar9@gmail.com)".format(version)
    )

    #adding options for numerical jobs
    parser.add_argument('-bib', type=str, help="DOI to get bibtex entry", metavar="DOI")
    parser.add_argument('-ref', type=str, help="DOI to get bibtex entries for all the references", metavar="DOI")
    parser.add_argument('-pdf', type=str, help="PDF file name(s) to get bibtex info", metavar="PDF", nargs='*')
    parser.add_argument('-ren', type=str, help="PDF file name(s) to rename with bibtex info", metavar="PDF", nargs='*')
    parser.add_argument('-dup', type=str, help="Bib file name(s) to find duplicates.", metavar="BIB", nargs='*')
    parser.add_argument('-o',   type=str, help="Output bib file", metavar="FILE")

    return parser





def writeBib(bibs, out):
    # write the bibtex information in file or stdout
    if out:
        with open(out,'w') as f:
            f.write(r"%commant{This file was created by kbib (https://github.com/Koushikphy/kbib)}")
            f.write("\n\n\n")
            f.write(bibs)
    else:
        print(bibs)


def CommandsGiven(args):
    # check if any commands are given
    for elem in ['bib','ref','pdf','ren','dup']:
        if getattr(args,elem):
            return True
    return False


def main():
    parser = createParser()
    args = parser.parse_args()

    if not CommandsGiven(args):
        parser.print_help()


    try:
        if args.bib:
            f,bib = get_bib(args.bib)
            if not f: raise
            bib = reconfigureBibs(bib)
            writeBib(bib,args.o)

        if args.ref:
            bib = getFullRefList(args.ref)
            writeBib(bib,args.o)

        if args.pdf:
            bibs = pdftobib(args.pdf)
            writeBib(bibs,args.o)

        if args.ren:
            renamePDF(args.ren)
        
        if args.dup:
            listDuplicates(args.dup)

    except AssertionError as e:
        print(e)

    except:
        print("Unable to parse bibtex information.")
        # raise


if __name__ == "__main__":
    main()

