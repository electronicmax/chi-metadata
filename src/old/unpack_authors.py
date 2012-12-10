
import csv,codecs
import printprogram as pp

def find_author(string,authors):
    string = string.lower()
    b = [a for a in authors if a.lastName.lower() in string and a.firstName.lower() in string]
    return b[0] if len(b) > 0 else None

def unpack(f="reviewers/authors_packed.csv"):
    authors = pp.get_program().authors.values()
    inf = csv.reader(codecs.open(f,'r','utf-8'))
    outf = codecs.open("%s-out.csv" % f,'w','utf-8')
    for author_row in inf:
        z = find_author(author_row[0], authors)
        if z :
            outf.write("%s\n" % ','.join([z.lastName,z.firstName,author_row[1]]))
        else:
            asplits = author_row[0].split(' ')
            outf.write("%s\n" % ','.join([' '.join(asplits[1:]), asplits[0], author_row[1], 'X' if len(asplits) > 2 else ' ']))
    outf.close()

if __name__ == '__main__':
    unpack()
    
            
                       
        


