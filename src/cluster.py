
import csv, fnmatch, re, os

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
    def __contains__(self, item): return self.get_canonical(item) is not None
    def _parse_cell(self,val):  return tuple([x.strip() for x in val.split('|')])
    def _serial_cell(self,cell): return '|'.join([x.strip() for x in cell])
    def load(self):
        ## loads the highest-incremented database to disk ##
        data = {}
        filename = self.get_current_db_filename()
        db = open(filename,'r')
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
        db = open(self.get_current_db_filename(),'w')
        writer = csv.writer(db)
        for canon,row in self._data.iteritems():
            rsers = [self._serial_cell(cell) for cell in row ]
            rcanon = self._serial_cell(canon)
            db.writerow([rcanon] + rsers)            
        db.close()
    def get_row(self,canon): return self._data[canon]
    def set_row(self,canon,row): self._data[canon] = row
    def add(self, new_affil, canon):
        assert self.get_canonical(canon) is not None, "error - key {0} not found".format(key)
        row = self.get_row(canon)
        if new_affil not in row: self.set_row(canon, new_affil.append(row))
    def get_canonical(self, canon):
        # looks up for an exact match
        return self._data.get(canon)
    def merge_rows(self,target_canon,src_canon):
        ## merges two lines
        self.add(src_canon,target_canon)
        self.set_row(target_canon, self.get_row(target_canon) + self.get_row(src_canon))
        del self._data[src_canon]
## 
def match(db, target):
    ## magic procedure that we have to write
    ## @param db is instance of AffiliationDB
    ## @param target is a 3-tuple ( Institution, City, Country ) 
    pass

def load_in(filename):
    db = load_db()
    for to_match in load_json(filename):
        c_match = match(db, candidate)
        if c_match not in db: db.add(candidate, c_match)
    db.save()

    
        
        
    
