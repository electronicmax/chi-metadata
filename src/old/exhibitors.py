
import csv

FILENAME = "program_data/exhibitors.csv"
TEMPLATE = """@:<@Exhibit title>%(title)s<\\a> - Booth %(booth)s
<@text>%(text)s
"""
TEMPLATE_LISTING = """<x@booth>%(booth)s<@><a$> \t <x@ExhibitTitle> %(title)s<a$>
"""


def run(template=TEMPLATE):
    r = csv.reader(open(FILENAME,'r'))
    rows = [x for x in r][1:]
    rows.sort(key=lambda r : r[1])
    for r in rows:
        print template % { "title" : r[0], "booth" : r[1], "text" : r[2] }

if __name__ == '__main__':
    run()
