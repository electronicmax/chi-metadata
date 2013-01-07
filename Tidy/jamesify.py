import csv,re

in_file = 'final-dictionary.txt'
out_file = 'final-dictionary-for-pcs.csv'

rows = [x for x in csv.reader(open(in_file,'r'))]
outf = open(out_file,'w')
out = csv.writer(outf)

def munge_canon(s):
    s = re.sub('\|US$','|United States',s)
    s = re.sub('\|UK$','|United Kingdom',s)
    return s

def munge_alt(s):
    return s.lower()

for r in rows:
    canon, alts = munge_canon(r[0]),[munge_alt(x) for x in r[1:]]
    for a in alts:
        out.writerow([canon,a])

outf.close()


    
    
