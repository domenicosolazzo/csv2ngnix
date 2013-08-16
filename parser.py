from __future__ import print_function
import csv
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--scheme', default="http", help="http or https", choices=['http', 'https'])
parser.add_argument('--upstream', help="Ngnix's upstream", required=True)
parser.add_argument('--csv', help="Input file", required=True)

parser.add_argument('--output', help="Output file", required=True)
parser.add_argument('--base_old_url', help="Base url for the old urls", required=True)
parser.add_argument('--base_new_url', help="Base url for the new urls", required=True)
parser.add_argument('--language', action="append", help="Languags for localizing the new urls")

args = parser.parse_args()

def printLocation(scheme, host, language, oldUrl, newUrl, f):
        if language:
            print("location = /" + language + oldUrl + "{", file=f)
        else:
            print("location = /" + oldUrl + "{", file=f)
        print("  proxy_pass " + scheme + "://" + host + newUrl, file=f)
        print("}", file=f)
        print(os.linesep, file=f)


def parseCSV(filename,  oldHostUrl, newHostUrl):
    urls = []
    urls_obsolete = []
    with open(filename, "rb") as f:
	print(f)
        reader = csv.reader(f)
        rows = [r for  r in reader if (r[0] and not (r[0] == "Next page"))  ][1:]
        for row in rows:
            oldUrl = row[0].replace(oldHostUrl, '').strip()
            newUrl = row[1].replace(newHostUrl, '').strip()
            isObsolete = row[3].lower() in ['true', 1, '1', 'obsolete']
            if isObsolete:
                urls_obsolete.append((oldUrl, newUrl))
            else:
                urls.append((oldUrl, newUrl))
    return (urls, urls_obsolete)
def translateToNgnix(outputFileName, scheme, host, urls, languages):    
    with open(outputFileName, "w") as f:
        for old, new in urls:
            if len(languages) > 0:
                for language in languages:
                    printLocation(scheme, host, language, old, new, f)
            else:
                printLocation(scheme, host, None, old, new, f)

scheme = args.scheme
upstream = args.upstream
csvFilename = args.csv
output = args.output
baseOldUrl = args.base_old_url
baseNewUrl = args.base_new_url
language = args.language

urls = parseCSV(csvFilename, baseOldUrl, baseNewUrl)
translateToNgnix(output, scheme, upstream, urls[0], language)
translateToNgnix(output+"_obsolete", scheme, upstream, urls[1], language)
