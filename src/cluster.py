
import csv

## database file

class AffiliationDB:
    DATABASE = "affiliation_mappings.csv"    
    def __init__(self):
        pass
    def __contains__(self, item):
        return self.get_canonical(item) is not None
    def _parse_cell(self,val):
        return tuple([x.strip() for x in val.split('|')])
    def _serial_cell(self,cell):
        return '|'.join([x.strip() for x in cell])
    def load(self):
        data = {}
        db = open(self.DATABASE,'r')
        rows = csv.reader(db)
        for line in rows:
            cells = [self._parse_cell(cell) for cell in line]
            data[cells[0]] = cells[1:]
        db.close()
        self._data = data
    def save(self):
        db = open(self.DATABASE,'w')
        writer = csv.writer(db)
        for canon,row in self._data.iteritems():
            rsers = [ self._serial_cell(cell) for cell in row ]
            rcanon = self._serial_cell(canon)
            db.writerow([rcanon] + rsers)            
        db.close()
    def get_row(self,canon):  return self._data[canon]
    def set_row(self,canon,row):  self._data[canon] = row
    def add(self, new_affil, canon):
        assert self.get_canonical(canon) is not None, "error - key {0} not found".format(key)
        row = self.get_row(canon)
        if new_affil not in row:
            self.set_row(canon, new_affil.append(row))
        pass
    def get_canonical(self, canon):
        # looks up for an exact match
        return self._data.get(canon)

## 
def match(db, target):
    ## magic q
    pass

def load_in(filename):
    db = load_db()
    for to_match in load_json(filename):
        c_match = match(db, candidate)
        if c_match not in db: db.add(candidate, c_match)
    db.save()

    
        
        
    
