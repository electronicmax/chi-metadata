
import string, collections, os

from chiProgram import *

# Use the latest dir
versions = glob.glob(os.sep.join([MAIN_DATA_DIR, "20*"]))
versions.sort()
chiProgram = CHIProgram(versions[-1], utf8ToHtmlEntities=True)

OUTPUT_DIRECTORY = os.sep.join(["output", "queries"])

def authorListTable():
    
    authors = chiProgram.authors.values()
    authors.sort(key=lambda x: (x.lastName.lower(), x.firstName.lower(), x.middleName.lower()))

    lfm = {}
    for author in authors:
        lastName   = author.lastName
        firstMiddleName = author.firstName + author.middleName
        firstMiddleName.strip()
        
        if (not lfm.has_key(lastName)):
            lfm[lastName] = set()
            
        lfm[lastName].add(firstMiddleName)
        
    html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
              <html>
              <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">"""
    
    html += '<table border="1">'
    
    lastNames = lfm.keys()
    lastNames.sort(key=lambda x: x.lower())
    
    for lastName in lastNames:
        firstNames = lfm[lastName]
        html += ('<tr><td valign="top">%s</td><td>%s</td></tr>' % 
                 (lastName, "<br />".join(firstNames)))
    
    html += '</table>'
    html += '</body></html>'

    fp = open(os.sep.join([OUTPUT_DIRECTORY, "authorListTable.html"]), "w")
    fp.write(html)
    fp.close()


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
                    
    fp = open(os.sep.join([OUTPUT_DIRECTORY, "authorConflicts.txt"]), "w")
    fp.write(output)
    fp.close()
    print output
                    


def authorsWithMultipleAffiliations():
    print "\n\n"
    print "AUTHORS WITH MULTIPLE AFFILIATIONS"
    for submissionId, submission in chiProgram.submissions.iteritems():
        for author in submission.authors:
            if (len(author.affiliations) > 1):
                print submissionId, author

def authorsListedMultipleTimes():
    print "\n\n"
    print "AUTHORS LISTED MULTIPLE TIMES"
    for submissionId, submission in chiProgram.submissions.iteritems():
        authorNames = [author.fullName() for author in submission.authors]
        if (len(set(authorNames)) != len(authorNames)):
            print submissionId, authorNames



def oddAffiliations():
    print "\n\n"
    print "AUTHORS WITH ODD AFFILIATIONS"
    puncSet = set("\/;")
    for affiliation in chiProgram.affiliations.itervalues():
        charsInName = set(unescape(affiliation.name))
        if (puncSet.intersection(charsInName)):
            for submission in affiliation.submissions:
                for author in submission.authors:
                    if (affiliation in author.affiliations):
                        print ", ".join([submission.id, author.fullName(), affiliation.name])
                        

def missingSessionChairs():
    print "\n\n"
    print "SESSIONS WITHOUT CHAIRS"
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
                if (not session.chair):
                    print day, slot, session.title



def subsWithAwards():
    print "\n\nSESSIONS WITH AWARDS"
    print 'ID, Type, Award'
    for submission in chiProgram.submissions.itervalues():
        if (submission.bestPaperAward):
            print '"' + '","'.join([str(submission.id), 
                              SUBMISSION_LABEL[submission.type], 
                              "Best"]) + '"'
        elif (submission.bestPaperNominee):
            print '"' + '","'.join([str(submission.id), 
                              SUBMISSION_LABEL[submission.type], 
                              "Honorable Mention"]) + '"'



def videoRecordingAuthors():
    
    headers = ["Contact First Name", "Contact Last Name", "Contact Email",
               "Paper Title", "Date", "Time"]
    rows = [headers]
    for session in chiProgram.sessionSequenceGenerator():
        if (session.avRequirements == "Video Record"):
            for submission in session.submissions:
                rows.append([submission.contactFirstName, submission.contactLastName, 
                             submission.contactEmail,
                             submission.rawFields["Title"], session.date, session.time])
    
    fp = open(os.sep.join([OUTPUT_DIRECTORY, "forManas.csv"]), "w")
    for row in rows:
        fp.write('"' + '", "'.join(row) + '"' + '\n')
    fp.close()


def presenterEmailsForRooms(rooms):
    for submission in chiProgram.submissions.itervalues():
        if (submission.session.room in rooms):
            print submission.authors[0].email


def authorsWithNameOrAffiliationVariations():
    print "\n\nAUTHORS WITH NAME/AFFILIATION VARIATION"
    # Quickly check for authors sharing first and last name
    d = collections.defaultdict(lambda: [])
    for author in chiProgram.authors.values():
        authorHash = author.firstName + author.lastName
        d[authorHash].append(author)
    for authorHash, authorList in d.iteritems():
        fullNames = set([author.fullName() for author in authorList])
        if (len(fullNames) > 1):
            print authorHash
            for author in authorList:
                print "\t", author
                for submission in author.submissions:
                    print "\t\t", submission.title


def authorOverlapWithLateVenues():
    print "\n\nAUTHOR OVERLAP WITH LATE VENUES"
    venuesToLookIn = [INTERACTIVITY, SIG_MEETING, DESIGN_COMP, RESEARCH_COMP, WORKS_IN_PROGRESS, VIDEOS]
    
    print "\nALREADY ACCEPTED AUTHORS"
    # Data from PCS
    firstAuthors = set()
    acceptedAuthors = set()
    for submission in chiProgram.submissions.values():
        if (submission.final):
            
            # Just first author
            author = submission.authors[0]
            authorHash = author.firstName.lower() + author.lastName.lower()
            firstAuthors.add(authorHash)
                
            # All authors
            for author in submission.authors:
                authorHash = author.firstName.lower() + author.lastName.lower()
                acceptedAuthors.add(authorHash)

    print len(firstAuthors), "different accepted first authors"
    print len(acceptedAuthors), "different accepted authors across all positions"
    
    for venue in venuesToLookIn:
        unacceptedSubmissions = [submission for submission in chiProgram.submissions.values() if ((submission.type == venue) and (not submission.final))]
        print "\nVENUE: %s -- %d submissions" % (SUBMISSION_LABEL[venue], len(unacceptedSubmissions))
        if (len(unacceptedSubmissions) == 0):
            continue
            
        uniqueAuthors = set()
        uniqueFirstAuthors = set()
        firstAuthorMatches = 0
        allAuthorMatches = 0
        for submission in unacceptedSubmissions:

            # first author here
            author = submission.authors[0]
            authorHash = author.firstName.lower() + author.lastName.lower()
            if (authorHash not in uniqueFirstAuthors):
                if (authorHash in acceptedAuthors):
                    firstAuthorMatches += 1
                uniqueFirstAuthors.add(authorHash)
                
            # across positions
            for author in submission.authors:
                authorHash = author.firstName + author.lastName
                if (authorHash not in uniqueAuthors):
                    if (authorHash in acceptedAuthors):
                        allAuthorMatches += 1
                    uniqueAuthors.add(authorHash)
                    
        print ("%d unique first authors, %d already accepted -> (%.2f%%)" % 
               (len(uniqueFirstAuthors), firstAuthorMatches, firstAuthorMatches / float(len(uniqueFirstAuthors)) * 100))
        print ("%d unique authors, %d already accepted -> (%.2f%%)" % 
               (len(uniqueAuthors), allAuthorMatches, allAuthorMatches / float(len(uniqueAuthors)) * 100))
    
    # Now go get authors for alt.chi because they decided not to use PCS
    csvReader = csv.reader(open(os.sep.join([MAIN_DATA_DIR, "alt_chi.csv"])))
    altChiSubmissionCount = 0
    firstAuthorMatches = 0
    uniqueFirstAuthors = set()
    for row in csvReader:
       # first author, we actually have first and last name
       firstAuthor = row[1]
       authorNameParts = firstAuthor.split()
       authorHash = authorNameParts[0].lower() + authorNameParts[-1].lower()
       uniqueFirstAuthors.add(authorHash)
       altChiSubmissionCount += 1
   
    print "\nVENUE: alt.chi -- %d submissions" % (altChiSubmissionCount)
    for authorHash in uniqueFirstAuthors:
       if (authorHash in acceptedAuthors):
           firstAuthorMatches += 1
    print ("%d unique first authors, %d already accepted -> (%.2f%%)" % 
           (len(uniqueFirstAuthors), firstAuthorMatches, firstAuthorMatches / float(len(uniqueFirstAuthors)) * 100))
    


def communitiesSet():
    core = set()
    featured = set()
    for submission in chiProgram.submissions.values():
        if (not submission.final):
            continue
            
        core.update(submission.coreCommunities)
        featured.update(submission.featuredCommunities)
        
    print "Core Communities:", core
    print "Featured Communities:", featured


def submissionsInMultipleSessions():
    print "\n\n"
    print "SUBMISSIONS WITH MULTIPLE SESSIONS"
    for submission in chiProgram.submissions.values():
        if (not submission.final):
            continue
            
        if (len(submission.session) > 1):
            if (submission.type not in [WORKSHOP, COURSE]):
                print "ERROR: ",
            print submission.type, len(submission.session), submission.title
            
            
    

#checkForAuthorConflicts()
#authorOverlapWithLateVenues()

#authorListTable()
#authorsWithMultipleAffiliations()
#authorsListedMultipleTimes()
#oddAffiliations()
#missingSessionChairs()

#subsWithAwards()
#videoRecordingAuthors()
#authorsWithNameOrAffiliationVariations()

#communitiesSet()
submissionsInMultipleSessions()