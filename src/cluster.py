
import csv, fnmatch, re, os, json, codecs

def decode(s):
    print s
    d1 = codecs.decode(s,'iso_8859_1','ignore')
    return d1.encode(encoding='utf_8')

def touch(fname, times=None):
    with file(fname, 'a'):
        os.utime(fname, times)
        
## database class for reading and writing affiliations

DBDIR = "db"

class AffiliationDB:
    def __init__(self):
        if self.get_current_db_filename() is None:
            self.create_new_db()
        self.load()
    def _get_file_id(self, name):
        return int(re.compile('affils-(\d+).csv').match(name).group(1))
    def get_current_db_filename(self):
        # finds the database with the highest version number
        matches = [f for f in os.listdir(DBDIR) if fnmatch.fnmatch(f,'affils-*.csv')]
        if len(matches) > 0:
            matches.sort(key=self._get_file_id)
            return matches[-1]
        return None
    def create_new_db(self):
        cur = self.get_current_db_filename()
        val = self._get_file_id(cur) if cur else 0
        filename = os.path.sep.join([DBDIR, 'affils-{0}.csv'.format(val + 1)])
        print "creating new database ", filename
        touch(filename)
    def __contains__(self, item): return self.get(item) is not None
    def _parse_cell(self,val):  return tuple([x.strip() for x in val.split('|')])
    def _serial_cell(self,cell):
        return '|'.join([x.strip() for x in cell])
    def load(self):
        ## loads the highest-incremented database to disk ##
        data = {}
        filename = os.path.sep.join([DBDIR, self.get_current_db_filename()])
        db = codecs.open(filename,'r','utf_8')
        print "opening ", filename
        rows = csv.reader(db)
        for line in rows:
            cells = [self._parse_cell(cell) for cell in line]
            data[cells[0]] = cells[1:]
        db.close()
        self._data = data
    def save(self, make_new=True):
        # saves the currently loaded dictionary to disk
        # _overwriting the most recent dictionary_ unless auto
        if make_new: self.create_new_db()
        filename = os.path.sep.join([DBDIR, self.get_current_db_filename()])
        db = codecs.open(filename,'w','utf_8')
        writer = csv.writer(db, dialect='excel')
        for canon,row in self._data.iteritems():
            print canon,row,type
            rsers = [self._serial_cell(cell) for cell in row ]
            rcanon = self._serial_cell(canon)
            try:
                writer.writerow([rcanon] + rsers)
            except ValueError as e:
                print "ERROR --------------------------------------- "
                pass            
        db.close()
    def get(self,canon): return self._data.get(canon)
    def set_row(self,canon,row): self._data[canon] = row
    def add(self, canon, new_affil=None):
        if new_affil == canon: return True
        if new_affil and canon and self.get(new_affil):
            # means we want to add new affil (and all its affiliations as an affil of canon)
            return self.merge_rows(canon, new_affil)
        # new affil we've never seen before
        row = self.get(canon) or []
        if new_affil and new_affil not in row:
            self.set_row(canon, row + [new_affil])
        else:
            self.set_row(canon, row)
    def merge_rows(self,target,src_canon):
        ## merges two lines
        new_row = [src_canon] + (self.get(target) or []) + (self.get(src_canon) or [])
        new_row = list(set(new_row)) # de-duplicate
        self.set_row(target, new_row)
        del self._data[src_canon]
## 
def match(db, target):
    ## magic procedure that we have to write
    ## @param db is instance of AffiliationDB
    ## @param target is a 3-tuple ( Institution, City, Country ) 
    pass

def load_json(json_file):
    return json.loads(''.join(codecs.open(json_file,'r','utf_8').readlines()))

def load_into_db(json_file,db):
    print "loading ", json_file
    jdata = load_json(json_file)
    def load(authors):
        auth = (author['Institution'], author['City'], author['Country'])
        if db.get(auth):  pass
        db.add(auth)
    [[load(author) for author in paper['primary'].values()] for paper in jdata]
    [[load(author) for author in paper['2ndary'].values()] for paper in jdata]

def load_entire_dir(dirname):
    db = AffiliationDB()    
    names = [load_into_db(os.path.sep.join([dirname,fname]),db) for fname in os.listdir(dirname) if fnmatch.fnmatch(fname,'*.out.json')]
    db.save()             

def load(filename):
    db = AffiliationDB()
    load_into_db(filename, db)
    db.save()

    
        
        
    
