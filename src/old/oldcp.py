import urllib2, cPickle, collections, operator, string, sys, time, csv, glob, os
from datetime import datetime
from pprint import pprint

import re, htmlentitydefs
import cgi

reload(sys)
sys.setdefaultencoding('utf_8')

MAIN_DATA_DIR = "program_data"
ORIGINAL_SUBMISSION_DATA_DIR = "original_submission_data"

#SUBMISSION TYPES
COURSE        = "cr"
CASE_STUDY    = "cs"
DOC_CONS      = "dc"
INTERACTIVITY = "in"
PAPER         = "paper"
PANEL         = "pl"
TOCHI         = "to"
WORKSHOP      = "wo"

ALT_CHI       = "al"
SIG_MEETING   = "si"
SPECIAL       = "sp"
VIDEOS        = "vi"

DESIGN_COMP       = "sd"
RESEARCH_COMP     = "sr"
GAME_COMP         = "SGC"
WORKS_IN_PROGRESS = "wp"

#SUBMISSION_TYPE_LABEL
SUBMISSION_LABEL = {COURSE : "Course",
                    CASE_STUDY : "Case Study",
                    DOC_CONS : "Doctoral Consortium",
                    INTERACTIVITY : "Interactivity", 
                    PAPER : "Paper",
                    PANEL : "Panel",
                    TOCHI : "ToCHI",
                    WORKSHOP : "Workshop",
                    ALT_CHI : "alt.chi",
                    SIG_MEETING : "SIG Meeting",
                    SPECIAL : "Special Events",
                    VIDEOS : "Videos",
                    DESIGN_COMP : "Student Design Competition",
                    RESEARCH_COMP : "Student Research Competition",
                    GAME_COMP : "Student Game Competition",
                    WORKS_IN_PROGRESS : "Works In Progress"}

ALL_SUBMISSION_TYPES = [COURSE, CASE_STUDY, DOC_CONS, INTERACTIVITY, PAPER, 
                        PANEL, TOCHI, WORKSHOP, ALT_CHI, SIG_MEETING, SPECIAL,
                        VIDEOS, DESIGN_COMP, RESEARCH_COMP, GAME_COMP,
                        WORKS_IN_PROGRESS]

# CORE COMMUNITIES
DESIGN = "design"
ENGINEERING = "engineering"
MANAGEMENT = "management"
USER_EXPERIENCE = "user experience"
CORE_COMMUNITIES = [DESIGN, ENGINEERING, MANAGEMENT, USER_EXPERIENCE]

# FEATURED COMMUNITIES
ARTS           = "arts"
CCI            = "cci"
GAMES          = "games"
HEALTH         = "health"
SUSTAINABILITY = "sustainability"
FEATURED_COMMUNITIES = [ARTS, CCI, GAMES, HEALTH, SUSTAINABILITY]

MULTIPLE_AFFILIATION_SEPARATOR = " / "


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def convertUtf8ToHtml(text):
    try:
        # First convert the few existing html entities to utf8
        # This has to be done because html codes are in the csv
        # If we just skipped to the next step then the codes will show up
        # literally. Ugh.
        converted = unescape(text)
        # Then convert to html entities
        converted = cgi.escape(converted).encode('ascii', 'xmlcharrefreplace')
        if (converted != text):
            #print "Converted", text, "to", converted
            pass
        return converted
    except:
        print text
        raise

COUNTRY_ABBREVs = {
    'united kingdom': 'UK',
    'england': 'UK',    
    'united states': 'USA',
    'us': 'USA',    
    'united states of america': 'USA'    
}

def abbreviate_country(s):
    if s.lower() in COUNTRY_ABBREVs:
        s = COUNTRY_ABBREVs[s.lower()]
    return convertUtf8ToHtml(s.strip())    

class Affiliation:
    
    def __init__(self, affiliation):
        
        self.name = affiliation
        self.submissions = []
        
    def assignedSubmissions(self):
        return [submission for submission in self.submissions if submission.session]
        
    def __str__(self):
        return self.name


class Author:

    def __init__(self, firstName, middleName, lastName, affiliations, email):

        self.firstName    = firstName
        self.middleName   = middleName
        self.lastName     = lastName
        self.affiliations = [Affiliation(affiliation) for affiliation in affiliations]
        self.email        = email
        
        self.submissions = []
        self.originalSubmissions = []

    def assignedSubmissions(self):
        return [submission for submission in self.submissions if submission.session]

    def fullName(self):

        full = []

        if (self.firstName):
            full.append(self.firstName)

        if (self.middleName):
            full.append(self.middleName)

        if (self.lastName):
            full.append(self.lastName)

        return " ".join(full)

    def allAffiliationsAsString(self, separator=MULTIPLE_AFFILIATION_SEPARATOR):
        return separator.join([str(a) for a in self.affiliations])

    def __str__(self):
        return "%s, %s" % (self.fullName(), self.allAffiliationsAsString())

    def __cmp__(self, other):
        if ((type(self) == type(other)) and 
            (self.firstName == other.firstName) and
            (self.middleName == other.middleName) and
            (self.lastName == other.lastName)):

            return 0
        else:
            return 1


class Submission:
    
    def __init__(self, fieldsAsDict, final=False, utf8ToHtml=False):
        self.rawFields = fieldsAsDict
        self.final = final
        self.utf8ToHtml = utf8ToHtml

        self.id       = None
        self.title    = None
        self.authors  = None
        self.type     = None
        self.cAndB    = None
        self.abstract = None

        self.contactFirstName = None
        self.contactLastName = None
        self.contactEmail = None

        self.session = []

        self.bestPaperNominee = False
        self.bestPaperAward   = False

        self.programNumber = None

        self.coreCommunities = []
        self.featuredCommunities = []

        self.acmLink = None

        self.parseData()
        

    def cleanUpSubmissionTitle(self, text):
        if (text.startswith("[NOT SUBMITTED] ")):
            return text[len("[NOT SUBMITTED] "):]
        return text

    def parseData(self):
        
        self.id = self.rawFields["ID"]
                
        self.title = convertUtf8ToHtml(self.cleanUpSubmissionTitle(self.rawFields["Title"]))

        self.contactEmail = self.rawFields["Contact Email"]
        self.contactFirstName = self.rawFields["Contact given name"]
        self.contactLastName = self.rawFields["Contact family name"]

        self.type = self.submissionTypeFromId()
        
        self.authors = self.parseOutAuthors()

        if (self.rawFields.has_key("Notes")):
            self.notes = self.rawFields["Notes"]
        else:
            self.notes = ""

        if (self.rawFields.has_key("Program Number")):
            self.programNumber = self.rawFields["Program Number"]

        if (self.rawFields.has_key("Contribution and Benefit Statement")):
            cAndB = self.rawFields["Contribution and Benefit Statement"]
            cAndB = cAndB.replace("\ ", "")
            if (cAndB and (cAndB[-1] == "\\")):
                cAndB = cAndB[:-1]
            self.cAndB = convertUtf8ToHtml(cAndB)
        elif (self.rawFields.has_key("Program Description")):
            cAndB = self.rawFields["Program Description"]
            cAndB = cAndB.replace("\ ", "")
            if (cAndB and (cAndB[-1] == "\\")):
                cAndB = cAndB[:-1]
            self.cAndB = convertUtf8ToHtml(cAndB)

        if (self.rawFields.has_key("Abstract")):
            self.abstract = convertUtf8ToHtml(self.rawFields["Abstract"])
        
        if (self.type == CASE_STUDY):
            if (self.final):
                self.longOrShort = self.rawFields["Long or Short"]
            else:
                self.longOrShort = self.rawFields["Long vs. Short"]
        elif (self.type == PAPER):
            if (self.final):
                self.paperOrNote = self.rawFields["Paper or Note"]
            else:
                self.paperOrNote = self.rawFields["Paper vs. Note"]
            
        if (self.rawFields.has_key("Awards")):
            award = self.rawFields["Awards"]
            if (award == "Honorable Mention"):
                self.bestPaperNominee = True
            elif (award == "Best"):
                self.bestPaperAward = True
            elif ((award == "") or (award == "None")):
                # No award
                pass
            else:
                print "ERROR: Unexpected award value:", award
        
        
    def submissionTypeFromId(self):
        a = ""
        for char in self.id:
            if (char not in string.digits):
                a = a + char
            else:
                break
        return a
        
    def parseOutAuthors(self):
        i = 1

        firstNameFieldFormat = "Given name %d"
        middleNameFieldFormat = "Middle initial %d"
        lastNameFieldFormat = "Family name %d"
        
        emailFieldFormat = "Email address %d"
        if (self.final):
            emailFieldFormat = "Email %d"

        rawAuthors = []
        while (i):
            
            if (not self.rawFields.has_key(firstNameFieldFormat % i)):
                break
            
            firstName   = convertUtf8ToHtml(self.rawFields[firstNameFieldFormat % i])
            middleName  = ""
            if (self.final):
                middleName  = convertUtf8ToHtml(self.rawFields[middleNameFieldFormat % i])
            lastName    = convertUtf8ToHtml(self.rawFields[lastNameFieldFormat % i])
            # emax changed this to add country
            affiliation = "%s, %s" % (convertUtf8ToHtml(self.rawFields["Primary Affiliation %d - Institution" % i]),abbreviate_country(self.rawFields["Primary Affiliation %d - Country" % i]))
            email       = self.rawFields[emailFieldFormat % i]
            if (lastName):
                if (rawAuthors and
                    (rawAuthors[-1][0] == firstName) and
                    (rawAuthors[-1][1] == middleName) and
                    (rawAuthors[-1][2] == lastName)):
                    # Author listed twice with multiple affiliations
                    rawAuthors[-1][3].append(affiliation)
                else:
                    # First appearance of author for this submission
        	        rawAuthors.append([firstName, middleName, lastName, [affiliation], email])
            else:
                if (affiliation):
                    # Extra check for authors with multiple affiliation but
                    # Author fields are only filled out once
                    rawAuthors[-1][3].append(affiliation)
                else:
                    # Completely empty Author entry, done looking for authors
        	        break
            i += 1

        authors = [Author(a[0], a[1], a[2], a[3], a[4]) for a in rawAuthors]

        return authors



class Session:
    
    def __init__(self, rawFields, chiProgram, utf8ToHtml=False):
        self.rawFields = rawFields
        self.chiProgram = chiProgram
        self.utf8ToHtml = utf8ToHtml
        
        self.id = None
        self.title = None
        self.type = None
        self.submissions = None
        self.room = None
        self.date = None
        self.time = None
        self.endTime = None
        self.chairs = None
        self.chairAffiliations = None
        self.avRequirements = None
        self.notes = None

        self.coreCommunities = []
        self.featuredCommunities = []

        self.parseData()
        
    def parseData(self):
        
        self.id          = self.rawFields["ID"]
        self.title       = convertUtf8ToHtml(self.cleanUpSessionTitle(self.rawFields["Title"]))
        
        self.submissions = []
        for subId in self.rawFields["Submission IDs"].split():
            if (subId in self.chiProgram.submissions):
                self.submissions.append(self.chiProgram.submissions[subId])
            else:
                print "    ERROR: Invalid submission id:", subId, "in session", self.title

        self.type        = self.getSessionType()
        self.room        = self.rawFields["Location"]
        if (not self.room):
            self.room = "TBD"
        
        self.date        = self.rawFields["Date"]
        self.time        = self.rawFields["Time"]
        
        self.endTime     = self.rawFields["End Time"]
        if (self.endTime.count(":") > 1):
            self.endTime = self.endTime.rsplit(":", 1)[0]

        self.chairs = [convertUtf8ToHtml(chair.strip()) for chair in self.rawFields["Chair(s)"].split(",") if (chair.strip() != "")]
        self.chairAffiliations = convertUtf8ToHtml(self.rawFields["Chair Affiliation(s)"])

        self.notes = self.rawFields["Notes"].strip()

        self.coreCommunities = self.getCoreCommunities()
        self.featuredCommunities = self.getFeaturedCommunities()

        for sub in self.submissions:
            sub.session.append(self)

    def cleanUpSessionTitle(self, title):
       if (title.startswith("Papers: ")):
           return title[len("Papers: "):]
       elif (title.startswith("Technical Presentations: ")):
           return title[len("Technical Presentations: "):]

       return title

    def getSessionType(self):
       subTypes = set()

       for sub in self.submissions:
           subTypes.add(SUBMISSION_LABEL[sub.type])

       subTypes = list(subTypes)
       subTypes.sort()

       if (subTypes):
           if (len(subTypes) > 1):
               return ", ".join(subTypes[:-1]) + " &amp; " + subTypes[-1]
           else:
               return subTypes[0]
       else:
           return ""


    def getCoreCommunities(self):
        comms = set()
        for sub in self.submissions:
            for comm in sub.coreCommunities:
                comms.add(comm)
        comms = list(comms)
        comms.sort()
        return comms

    def getFeaturedCommunities(self):
        comms = set()
        for sub in self.submissions:
            for comm in sub.featuredCommunities:
                comms.add(comm)
        comms = list(comms)
        comms.sort()
        return comms


def listMultipleAppearances(keys):
    count = collections.defaultdict(lambda: 0)
    for k in keys:
        count[k] += 1
    for k, c in count.iteritems():
        if (c > 1):
            print "    WARNING: '%s' key appears %d times" % (k, c)


class CHIProgram:

    def __init__(self, dataDir, utf8ToHtmlEntities=False):

        print "Parsing data from:", dataDir
        self.dataDir = dataDir
        self.utf8ToHtml = utf8ToHtmlEntities

        #Affiliation dictionary index by string representation of affiliation
        self.affiliations = {}
        
        #Author dictionary index by string representation of author
        self.authors = {}

        #Submissions dictionary indexed by submission ID from csv file
        self.submissions = {}
        
        #Original submissions dictionary, index by submission ID from csv file
        self.originalSubmissions = {}
        
        #Session dictionary, 3-level index Date, Time, Room => Session Object
        self.sessions = {}
        self.sessionsById = {}

        self.parseOriginalSubmissions()
        self.parseSubmissions()
        self.addCommunitiesInfo()
        
        self.parseSessions()
        #self.removeSubmissionsNotInSessions()

        self.consolidateAuthors()
        self.consolidateAffiliations()
        
        self.connectAuthorsWithSubmissions()
        self.connectAffiliationsWithSubmissions()
        
        self.addExtraAuthorsFromDummySubmissions()
        
        self.handleDuplicateSessions()
        
        
    def parseOriginalSubmissions(self):

        print "Parsing Original Submissions..."
        files = glob.glob(os.sep.join(["%s", ORIGINAL_SUBMISSION_DATA_DIR, "*_submissions.csv"]) % self.dataDir)

        for submissionFile in files:
            print "  %s" % submissionFile.split(os.sep)[-1]
            csvReader = csv.reader(open(submissionFile))
            # Skip over header and first blank line, read in fields, skip next blank line
            csvReader.next()
            csvReader.next()
            csvFields = csvReader.next()
            csvReader.next()

            listMultipleAppearances(csvFields)
            for row in csvReader:
                row = [v.strip() for v in row]
                info = dict(zip(csvFields, row))
                submission = Submission(info, final=False, utf8ToHtml=self.utf8ToHtml)
                if (submission.authors):
                    self.submissions[submission.id] = submission


    def parseSubmissions(self):

        print "Parsing Submissions..."
        files = glob.glob(os.sep.join(["%s", "*_submissions.csv"]) % self.dataDir)

        for submissionFile in files:
            print "  %s" % submissionFile.split(os.sep)[-1]
            csvReader = csv.reader(open(submissionFile))
            # Skip over header and first blank line, read in fields, skip next blank line
            csvReader.next()
            csvReader.next()
            csvFields = csvReader.next()
            csvReader.next()

            listMultipleAppearances(csvFields)
            for row in csvReader:
                row = [v.strip() for v in row]
                info = {}
                for key, value in zip(csvFields, row):
                    if (key not in info):
                        info[key] = value
                submission = Submission(info, final=True, utf8ToHtml=self.utf8ToHtml)
                if (submission.authors):
                    self.submissions[submission.id] = submission


    def parseSessions(self):

        print "Parsing Sessions..."
        files = glob.glob(os.sep.join(["%s", "*_sessions.csv"]) % self.dataDir)

        for sessionFile in files:
            print "  %s" % sessionFile.split(os.sep)[-1]
            sessionsReader = csv.reader(open(sessionFile))
            sessionsFields = sessionsReader.next()

            listMultipleAppearances(sessionsFields)

            for sessionI, row in enumerate(sessionsReader):
                row = [v.strip() for v in row]

                # Create dictionary of this row
                rowDict = {}
                for key, value in zip(sessionsFields, row):
                    if (key not in rowDict):
                        rowDict[key] = value
                    
                if (not rowDict["Date"]):
                    continue

                session = Session(rowDict, self, utf8ToHtml=self.utf8ToHtml)
                if (session.title == "Unassigned Submissions"):
                    continue
                    
                # Course/Workshop/SigMeeting titles need to be adjusted
                if (session.submissions and 
                    session.submissions[0].type in [PANEL, SIG_MEETING, WORKSHOP]):
                    session.title = session.submissions[0].title
                    
                # Had to do this because Ed Chi changed the wrong files
                if (session.submissions and 
                    session.submissions[0].type in [COURSE]):
                    session.submissions[0].title = session.title
            
                if (not session.submissions):
                    print "    WARNING:", session.title, "has no submissions"

                if (not self.sessions.has_key(session.date)):
                    self.sessions[session.date] = {}

                if (not self.sessions[session.date].has_key(session.time)):
                    self.sessions[session.date][session.time] = {}

                if (not self.sessions[session.date][session.time].has_key(session.room)):
                    self.sessions[session.date][session.time][session.room] = []
                
                self.sessions[session.date][session.time][session.room].append(session)
                self.sessionsById[session.id] = session


    def removeSubmissionsNotInSessions(self):
        toRemove = []
        for submissionId, submission in self.submissions.iteritems():
            if (submission.session == None):
                toRemove.append(submissionId)
        for submissionId in toRemove:
            del self.submissions[submissionId]
        

    def sessionSequenceGenerator(self):
        dates = self.sessions.keys()
        # sort by date value, have to extract date and convert to int because 
        # single digit dates don't have a leading 0
        dates.sort(key=lambda x: int(x.split()[1][:-1]))
        #Skipping workshop days May 7th and 8th
        dates = dates[2:]

        for day in dates:

            timeslots = self.sessions[day].keys()
            timeslots.sort(key=lambda x: int(x[:2]))

            for slot in timeslots:

                authorsInSlot = {}

                rooms = self.sessions[day][slot].keys()

                for room in rooms:
                    sessions = self.sessions[day][slot][room]
                    for session in sessions:
                        yield session
        


    def consolidateAuthors(self):
        for submission in self.submissions.itervalues():
            subAuthors = submission.authors
            authorRefs = []
            for author in subAuthors:
                authorHash = author.firstName.lower() + author.lastName.lower() + author.allAffiliationsAsString()
                if (not self.authors.has_key(authorHash)):
                    self.authors[authorHash] = author
                else:
                    existingAuthor = self.authors[authorHash]
                    if ((not existingAuthor.middleName) and
                        (author.middleName)):
                        existingAuthor.middleName = author.middleName
                authorRefs.append(self.authors[authorHash])
            submission.authors = authorRefs


    def consolidateAffiliations(self):
        for submission in self.submissions.itervalues():
            subAuthors = submission.authors
            for author in subAuthors:
                consolidated = []
                for affiliation in author.affiliations:
                    affiliationHash = str(affiliation)
                    if (not self.affiliations.has_key(affiliationHash)):
                        self.affiliations[affiliationHash] = affiliation
                    consolidated.append(self.affiliations[affiliationHash])
                author.affiliations = consolidated


    def connectAuthorsWithSubmissions(self):
        for submission in self.submissions.itervalues():
            subAuthors = submission.authors
            for author in subAuthors:
                author.submissions.append(submission)


    def connectAffiliationsWithSubmissions(self):
        for submission in self.submissions.itervalues():
            subAuthors = submission.authors
            for author in subAuthors:
                for affiliation in author.affiliations:
                    if (submission not in affiliation.submissions):
                        affiliation.submissions.append(submission)
        

    def cheap(self, a, b):

        aWords = a.split(" ")
        bWords = b.split(" ")
        bWordsCt = len(bWords)

        matches = 0.0
        for wa in aWords:
            try:
                bWords.remove(wa)
                matches += 1
            except ValueError:
                # Word not found
                pass

        return matches / max(len(aWords), bWordsCt)
    
    def findClosestTitle(self, title, titles):
        
        maxMatch = 0
        result = None
        for checkAgainst in titles:
            match = self.cheap(title, checkAgainst)
            if (match > maxMatch):
                maxMatch = match
                result = checkAgainst
        
        return (maxMatch, result)
        

    def addACMLinks(self):
    
        linkD = {}
        URL_START = "http://portal.acm.org/"
        
        soup = BS(open("toc.html").read())
        anchors = soup.findAll(lambda tag: ((tag.name == "a") and (tag.has_key('href')) and ("citation" in tag["href"])))
        for a in anchors:
            title = str(a.contents[0]).lower()
            linkD[title] = URL_START + a['href']
            
        soup = BS(open("ea.html").read())
        anchors = soup.findAll(lambda tag: ((tag.name == "a") and (tag.has_key('href')) and ("citation" in tag["href"])))
        for a in anchors:
            title = str(a.contents[0]).lower()
            linkD[title] = URL_START + a['href']
        
        matchDistribution = collections.defaultdict(lambda: [])
        for submission in self.submissions.itervalues():
            if (submission.type != COURSE):
                title = submission.title.lower()
                match, closest = self.findClosestTitle(title, linkD.iterkeys())
                matchDistribution[match].append((title, closest))
                if ((match > 0.45) and closest):
                    submission.acmLink = linkD[closest]
                
    
    def addCommunitiesInfo(self):
        self.addPaperCommunitiesInfo()
        self.addOtherCommunitiesInfo()

        
    def addOtherCommunitiesInfo(self):
        communitiesFilename = os.sep.join([MAIN_DATA_DIR, "communities.csv"])
        if (not os.path.exists(communitiesFilename)):
            print "No communities info for non-papers in", MAIN_DATA_DIR
            return

        print "Adding communities info to non-paper submissions"
        csvReader = csv.reader(open(communitiesFilename))
        for row in csvReader:
            if (not row):
                # Empty row
                continue
                
            submissionId = row[0]
            if (submissionId not in self.submissions):
                # Header row
                continue
            submission = self.submissions[submissionId]
            
            coreCommunities = set()
            featuredCommunities = set()
            for comm in row[1].split(","):
                comm = comm.strip().lower();
                if (comm in CORE_COMMUNITIES):
                    coreCommunities.add(comm)
                elif (comm in FEATURED_COMMUNITIES):
                    featuredCommunities.add(comm)
                elif (comm):
                    print "INVALID COMMUNITY: '%s'" % comm
                    
            coreCommunities = list(coreCommunities)
            coreCommunities.sort()
            submission.coreCommunities = coreCommunities
                    
            featuredCommunities = list(featuredCommunities)
            featuredCommunities.sort()
            submission.featuredCommunities = featuredCommunities


    def addPaperCommunitiesInfo(self):
        communitiesFilename = os.sep.join([MAIN_DATA_DIR, "paper_communities.csv"])
        if (not os.path.exists(communitiesFilename)):
            print "No communities info for papers in", MAIN_DATA_DIR
            return
            
        print "Adding communities info to paper submissions"
        csvReader = csv.reader(open(communitiesFilename))
        for row in csvReader:
            if (not row):
                # Empty row
                continue
                
            submissionId = row[0]
            if (submissionId not in self.submissions):
                # Header row
                continue
            submission = self.submissions[submissionId]
            
            coreComms = set()
            featuredComms = set()
            for comm in row[1].split(","):
                comm = comm.strip().lower();
                if (comm in CORE_COMMUNITIES):
                    coreComms.add(comm)
                elif (comm in FEATURED_COMMUNITIES):
                    featuredComms.add(comm)
                elif (comm):
                    print "INVALID COMMUNITY: '%s'" % comm
                    
            coreComms = list(coreComms)
            coreComms.sort()
            submission.coreCommunities = coreComms
                    
            featuredComms = list(featuredComms)
            featuredComms.sort()
            submission.featuredCommunities = featuredComms
        

    def addExtraAuthorsFromDummySubmissions(self):
        print "Handling cases of > 10 authors"
        dummySubmissions = []
        for submission in self.submissions.itervalues():
            if ("combine" in submission.notes):
                dummySubmissionId = submission.notes[len("combine: "):].split(" ", 1)[0]
                dummySubmission = self.submissions[dummySubmissionId]
                print "  from dummy submission %s to %s" % (dummySubmission.id, submission.id)
                submission.authors.extend(dummySubmission.authors)
                dummySubmissions.append(dummySubmission)
        
        # Remove dummy submissions from data so they are not used in program generation
        for submission in dummySubmissions:
            
            # remove from relevant sessions
            for session in submission.session:
                session.submissions.remove(submission)
                
            # remove from submission dict
            del self.submissions[submission.id]
            

    def handleDuplicateSessions(self):
        print "Handling duplicating sessions"
        for session in self.sessionSequenceGenerator():
            if (not session.notes):
                continue
                
            words = session.notes.lower().split()
            dupCount = words.count("dup:")
            start = 0
            while (dupCount):
                position = words.index("dup:", start)
                sessionToDup = words[position+1]
                dupCount -= 1
                start = position + 1
                if (sessionToDup in self.sessionsById):
                    print "  adding submissions from session %s to %s" % (sessionToDup, session.id)
                    sessionToDup = self.sessionsById[sessionToDup]
                    session.submissions.extend(sessionToDup.submissions)
                    session.type = session.getSessionType()
                else:
                    print "  WARNING session to duplicate (%s) does not exist" % sessionToDup
                


if __name__ == "__main__":
    # Use the latest dir
    versions = glob.glob(os.sep.join([MAIN_DATA_DIR, "20*"]))
    versions.sort()
    chiProgram = CHIProgram(versions[-1], utf8ToHtmlEntities=True)
            
    
    
    
    
