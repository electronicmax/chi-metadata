#!/usr/bin/python 

import csv, sys, re, json
from collections import defaultdict

primary_re = re.compile('Primary Affiliation (\d+) - (\S+)$')
second_re = re.compile('Secondary Affiliation \(optional\) (\d+) - (\S+)$')

def header_idxs(headers, are=primary_re):
    return [(i, are.match(headers[i]).groups()[0], are.match(headers[i]).groups()[1]) for i in range(len(headers)) if are.match(headers[i])]

def compile_affils(row, his):
    affils = defaultdict(dict)
    for hi in his:
        col, author, field = hi
        # print author,"-",field," row[col].strip():", len(row[col].strip()) > 0, " - ",affils.get(author)
        if len(row[col].strip()) > 0 or affils.get(author):
            affils[author][field] = row[col]
    return dict(affils)

def read_file(name):
    ff = csv.reader(open(name,'rU'))
    rows = [x for x in ff]
    trash, trash, headers  = rows[0],rows[1],rows[2]
    submissions = [r for r in rows[3:] if len(r)]
    return [{'primary': compile_affils(s, header_idxs(headers)), '2ndary': compile_affils(s, header_idxs(headers,are=second_re))} for s in submissions]
            

def process(name='../from-pcs/4-dec-2013/listOfSubmissions (10).csv'):
    infile = name
    outfile = "{0}.out.json".format(infile[:-4])
    print "writing to outfile - ", outfile
    out = open(outfile,'w')
    z = read_file(infile)
    out.write(json.dumps(z))
    out.close()

def test():
    return process()

if __name__ == '__main__':
    fname = sys.argv[1]
    print 'loading from file ', fname
    process(fname)
