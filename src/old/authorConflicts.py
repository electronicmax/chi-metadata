import string, collections

from chiProgram import *

# Use the latest dir
versions = glob.glob(os.sep.join(["program_data", "20*"]))
versions.sort()
chiProgram = CHIProgram(versions[-1], utf8ToHtmlEntities=True)


def checkForAuthorConflicts():

    output = ""
    output += "\n\nAUTHOR CONFLICTS"
    
    dates = chiProgram.sessions.keys()
    # sort by date value, have to extract date and convert to int because 
    # single digit dates don't have a leading 0
    dates.sort(key=lambda x: int(x.split()[1][:-1]))
    #Skipping workshop days May 7th and 8th
    dates = dates[2:]

    for day in dates:
        
        timeslots = chiProgram.sessions[day].keys()
        timeslots.sort(key=lambda x: int(x[:2]))
        
        for slot in timeslots:
            
            authorsInSlot = {}
            
            rooms = chiProgram.sessions[day][slot].keys()
            
            for room in rooms:
                session = chiProgram.sessions[day][slot][room]
            
                if (session.submissions):
                    for submission in session.submissions:
                        authors = submission.authors
                        for a in authors:
                            authorKey = "%s %s" % (a.firstName, a.lastName)
                            if (not authorsInSlot.has_key(authorKey)):
                                authorsInSlot[authorKey] = set([session.title])
                            else:
                                authorsInSlot[authorKey].add(session.title)
                    
            conflictFoundYet = False
            for author in authorsInSlot.keys():
                sessionsForAuthor = authorsInSlot[author]
                if (len(sessionsForAuthor) > 1):
                    if (not conflictFoundYet):
                        output += "\n\nConflicts for %s at %s\n" % (day, slot)
                        conflictFoundYet = True
                    output += author + " is in \"" +  "\", \"".join(sessionsForAuthor) + "\"\n"
                    
    print output


checkForAuthorConflicts()