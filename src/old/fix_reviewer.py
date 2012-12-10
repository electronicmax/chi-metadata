import chiProgram as cP
import printprogram as pp
import csv

def build_dict(authors):
    return dict([(a.email, a) for a in authors])

def process(row, authors, ln_col, fn_col, email_col, affil_col, country_col):
    # find the email address
    email = row[int(email_col)].strip().lower() # filter(lambda x : "@" in x,row)[0]
    if email not in authors:
        return [ row[int(ln_col)], row[int(fn_col)], row[int(email_col)], row[int(affil_col)], row[int(country_col)] ]
    a = authors[email]
    countrysplit = a.affiliations[0].name.split(',')
    return [a.lastName, a.firstName, a.email, ','.join(countrysplit[0:-1]).strip(), countrysplit[-1].strip()]

def fix_file(fname,ln_col,fn_col,email_col,affil_col,country_col,proceedings=None):
    if proceedings == None: proceedings = pp.get_program()
    authors_dict = build_dict(proceedings.authors.values())
    print "reading %s ", fname
    rin = csv.reader(open(fname,'rU'))
    fout = open("%s-out.csv"% fname,'w')
    wout = csv.writer(fout)
    rows = [wout.writerow(
            map(lambda x : cP.unescape(x), process(row,authors_dict,ln_col,fn_col,email_col,affil_col,country_col))
            ) for row in rin if len(row) > 0]
    fout.close()

if __name__ == '__main__':
    import sys
    print "fixing file", sys.argv[1]
    if len(sys.argv) < 7:
        print "need infile, lncol, fn_col, email_col, affil_col, country_col"
    fix_file(*sys.argv[1:])
    
    




    


