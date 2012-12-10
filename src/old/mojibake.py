
import printprogram

def find_mojibake(program=None, check_abstract=False):
    if program is None:
        program = printprogram.get_program()
    bake = '&#65533'
    baked = []
    for p in program.submissions.values():
        ghost = False
        if bake in p.title:
            print p.id, "TITLE ", p.title
            ghost = True
        bauthors = [ba for ba in p.authors if bake in ba.fullName()]
        if len(bauthors) > 0:
            print p.id, "AUTHOR ", [b.fullName() for b in bauthors]
            ghost = True

        baffils = reduce(lambda x,y: x+y, [[ba for ba in a.affiliations if bake in ba.name] for a in p.authors], [])
        if len(baffils) > 0:
            print p.id, "AUTHOR AFFIL ", [b.name for b in baffils]
            ghost = True

        if (p.cAndB and bake in p.cAndB): 
            print p.id, "C AND B ", p.cAndB
            ghost = True

        if (check_abstract and p.abstract and bake in p.abstract):
            print p.id, " ABSTRACAT ", p.abstract
            ghost = True            
            
        if ghost: baked.append(p)

    return baked

def find_mojibake_abstracts(program=None):
    find_mojibake(program,True)
