#!/usr/bin/python 

import csv, sys, re
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

def read_file(name='../from-pcs/4-dec-2013/listOfSubmissions (10).csv'):
    ff = csv.reader(open(name,'rU'))
    rows = [x for x in ff]
    trash, trash, headers  = rows[0],rows[1],rows[2]
    submissions = [r for r in rows[3:] if len(r)]
    return [compile_affils(s, header_idxs(headers)) for s in submissions]

def test():
    return read_file()

# if __name__ == '__main__':
#     fname = sys.argv[1]
#     print 'loading from file ', fname
#     ff = csv.reader(open(fname,'rU'))
#     rows = [x for x in ff]
#     print len(rows)
#     trash, trash, headers  = rows[0],rows[1],rows[2]
#     submissions = rows[3:]
#     # print submissions
#     his = header_idxs(headers)
#     print ' headers ', his
