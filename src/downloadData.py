import mechanize, time, os, getpass, thread

import chiProgram

VENUE_TO_SUBMISSION_TYPE = {
    "Works-in-Progress" : chiProgram.WORKS_IN_PROGRESS,
	"Interactivity" : chiProgram.INTERACTIVITY,
	"SIG Meetings" : chiProgram.SIG_MEETING,
	"SRC" : chiProgram.RESEARCH_COMP,
	"SDC" : chiProgram.DESIGN_COMP,
    "SGC" : chiProgram.GAME_COMP,
	"alt.chi" : chiProgram.ALT_CHI,
	"Special Events" : chiProgram.SPECIAL,
	"Videos" : chiProgram.VIDEOS,
	"TOCHI" : chiProgram.TOCHI,
	"Workshops" : chiProgram.WORKSHOP,
	"Doctoral Consortium" : chiProgram.DOC_CONS,
	"Panels" : chiProgram.PANEL,
	"Case Studies" : chiProgram.CASE_STUDY,
	"Courses" : chiProgram.COURSE,
	"Papers and Notes" : chiProgram.PAPER
}

VENUES_TO_DOWNLOAD = VENUE_TO_SUBMISSION_TYPE.keys();

#DOWNLOAD_ORIGINAL_FOR_VENUES = VENUE_TO_SUBMISSION_TYPE.keys();
DOWNLOAD_ORIGINAL_FOR_VENUES = []

NUM_THREADS = 20
runningThreadLock = thread.allocate_lock()
runningThreads = 0

jobLock = thread.allocate_lock()
jobs = []

def main():
    startTime = time.time()

    createDataDir()
    createJobs()
    
    username = raw_input("PCS Username: ")
    password = getpass.getpass("PCS Password: ")

    createWorkerThreads(username, password)
    waitForThreadsToFinish()

    print "Total time:", (time.time() - startTime)


def waitForThreadsToFinish():
    time.sleep(2)
    while (runningThreads > 0):
        time.sleep(2)


def createDataDir():
    # Create main data directory if missing
    if (not os.path.exists(chiProgram.MAIN_DATA_DIR)):
        os.mkdir(chiProgram.MAIN_DATA_DIR)
    os.chdir(chiProgram.MAIN_DATA_DIR)
    
    # Create directory for today if missing
    dirName = time.strftime("%Y_%m_%d")
    if (not os.path.exists(dirName)):
        os.mkdir(dirName)
    os.chdir(dirName)
    
    # Create sub directory for original submission data 
    if (not os.path.exists(chiProgram.ORIGINAL_SUBMISSION_DATA_DIR)):
        os.mkdir(chiProgram.ORIGINAL_SUBMISSION_DATA_DIR)


def createJobs():
    for venue in VENUE_TO_SUBMISSION_TYPE.keys():
        if (venue in VENUES_TO_DOWNLOAD):
            jobs.append([venue, downloadFinalSubmissionData])
            jobs.append([venue, downloadSessionData])
            if (venue in DOWNLOAD_ORIGINAL_FOR_VENUES):
                jobs.append([venue, downloadOriginalSubmissionData])


def incRunningThreads():
    global runningThreads
    runningThreadLock.acquire()
    runningThreads += 1
    runningThreadLock.release();

    
def decRunningThreads():
    global runningThreads
    runningThreadLock.acquire()
    runningThreads -= 1
    print "  %d thread(s) left" % runningThreads
    runningThreadLock.release();


def createWorkerThreads(username, password):
    for i in xrange(NUM_THREADS):
        thread.start_new_thread(workerThread, (username, password))

def workerThread(username, password):

    incRunningThreads()
    
    br = mechanize.Browser()
    br.open("https://precisionconference.com/~sigchi/login")

    login(br, username, password)
    gotoChairingPage(br)
    
    while (True):
        jobLock.acquire()
        if (jobs):
            venue, downloadMethod = jobs.pop()
            print "  %d job(s) left"  % (len(jobs))
            jobLock.release()
            venueType = VENUE_TO_SUBMISSION_TYPE[venue]
            gotoVenuePage(br, venue)
            downloadMethod(br, venueType)
            br.back()
        else:
            jobLock.release()
            break

    decRunningThreads()
    
    
def gotoVenuePage(br, venue):
    links = br.links()
    for link in links:
        if (venue in link.text and 'publications' in link.text):
            br.follow_link(link)


def login(br, username=None, password=None):
    #print "Logging in"
    br.select_form(name="logon")
    if (username):
        br["userLoginID"] = username
        br["password"] = password
    else:
        br["userLoginID"] = raw_input("PCS Username: ")
        br["password"] = getpass.getpass("PCS Password: ")
    br.submit()
    

def gotoChairingPage(br):
    #print "Going to chairing page"
    try:
        link = br.find_link(text="chairing")
        br.follow_link(link)
    except (mechanize.LinkNotFoundError):
        #print "  Already on chairing page"
        pass


def downloadOriginalSubmissionData(br, venueType):
    #print "    Downloading original %s submission data" % venueType
    try:
        link = br.find_link(text="Original submission data")
        br.follow_link(link)
        submissionData = br.response().read()
        filename = os.sep.join([chiProgram.ORIGINAL_SUBMISSION_DATA_DIR, "%s_submissions.csv" % venueType])
        fp = open(filename, "w")
        fp.write(submissionData)
        fp.close()
        br.back()
    except (mechanize.LinkNotFoundError):
        print "ERROR: No original submission data link"
        print list(br.links())


def downloadFinalSubmissionData(br, venueType):
    #print "    Downloading final %s submission data" % venueType
    try:
        link = br.find_link(text="Final submission data")
        br.follow_link(link)
        submissionData = br.response().read()
        fp = open("%s_submissions.csv" % venueType, "w")
        fp.write(submissionData)
        fp.close()
        br.back()
    except (mechanize.LinkNotFoundError):
        print "ERROR: No final submission data link", venueType
        

def downloadSessionData(br, venueType):
    #print "    Downloading %s session data" % venueType
    try:
        link = br.find_link(text="Sessions")
        br.follow_link(link)
        try:
            link = br.find_link(text="Download these sessions")
            br.follow_link(link)
            sessionData = br.response().read()
            fp = open("%s_sessions.csv" % venueType, "w")
            fp.write(sessionData)
            fp.close()
            br.back()
        except (mechanize.LinkNotFoundError):
            # No problem here, not all venues have a sessions
            pass
        br.back()
    except (mechanize.LinkNotFoundError):
        print "ERROR: No sessions link"
        

if __name__ == "__main__":
    main()
