import wikipedia
import random
import json
import csv
from datetime import datetime

# Classes for Dexter DOF Swarm
    # AntColony - Colony of ants
    # AntMem - ants
    # PageClass - Pages
    # PathLink - Links between Pages

class AntColony:
    def __init__(self, startS, endS, stepM = 20, antM = 8, conM = 2, dBase = None, csvFile = None):
        # Parameter Setup
        self.startPoint = startS
        self.endPoint = endS
        self.max_steps = stepM
        self.max_ants = antM-1
        self.concurrent = conM
        self.db = dBase
        self.cFile = csvFile
        # ----------------------------------------------------------------------
        # AntColony Optimization Values
        self.setupMaxDrop = 3500
        self.setupChangeDrop = 500
        self.antMaxDrop = 32768
        self.antFullChance = 20
        self.antRandChance = 2
        self.antTwoChance = 2
        # Special Parameter Setup
        # If the parameters below are (< 0) They will be subtracted from previous values
        # If the parameters below are (< 0) They will be multiplied by the previous values
        self.timeEvapRate = 0.75
        self.antChangeDrop = 0.5
        # ----------------------------------------------------------------------
        # Init
        self.resetSeed = random.randint(0,50000)
        self.allPages = {}
        self.currentTime = 0
        self.totalAnts = 0
        self.histOptions = 0
        self.ants = []
        for nAnt in range(0, self.concurrent):
            self.ants.append(AntMem(self.startPoint,self.endPoint, self.max_steps, self.getAntSetupSettings()))
            self.totalAnts += 1

        self.allPages[self.startPoint] = PageClass(self.startPoint, self.db)
        self.allPages[self.startPoint].firstSetup(self, self.endPoint, self.currentTime, self.resetSeed, self.db)


    # Returns page from colony dictionary - If page does not exist, None is returned
    def getPage(self, pgStr):
        if pgStr in self.allPages:
            return self.allPages[pgStr]
        else:
            return None

    def getSetupPherSettings(self):
        return [self.setupMaxDrop, self.setupChangeDrop]

    def getAntSetupSettings(self):
        return [self.antMaxDrop, self.antChangeDrop, self.antFullChance, self.antRandChance, self.antTwoChance]

    def getEvapRate(self):
        return self.timeEvapRate

    def getColonySize(self):
        return self.max_ants

    def getPathHist(self):
        return self.histOptions

    def checkPage(self, pgStr):
        return pgStr in self.allPages

    def setPathHist(self, histOpt):
        self.histOptions = histOpt

    # Adds PageClass object to colony dictionary
    def addPage(self, adPage):
        pgStr = adPage.getPageName()
        self.allPages[pgStr] = adPage

    def run(self, steps = None):
        # If steps = None, run until all ants are dead
        # If steps given, run only number of time stps requested
        if steps != None:
            endTime = self.currentTime + steps
        else:
            endTime = self.currentTime

        while len(self.ants) > 0 and (steps == None or self.currentTime < endTime):
            # Current Information for this cycle (number of current ants + counter)
            aliveAnts = len(self.ants)
            antNum = 0
            # One Timestep cycle through all alive ants. Accounts for ant removal/replacement due to death or success
            while antNum < aliveAnts:
                if self.ants[antNum].isDead():
                    self.ants[antNum].postMortem(self, self.db, self.cFile)
                    # Ant replacement (Colony has additional ants)
                    if self.totalAnts <= self.max_ants:
                        self.ants[antNum] = AntMem(self.startPoint, self.endPoint, self.max_steps, self.getAntSetupSettings())
                        self.totalAnts = self.totalAnts + 1
                    # Ant Removal (Colony has no more ants)
                    else:
                        self.ants.pop(antNum)
                        antNum -= 1
                        aliveAnts -= 1
                else:
                    self.ants[antNum].move(self, self.currentTime, self.resetSeed, self.db)
                antNum += 1

            self.currentTime += 1


class PageClass:
    def __init__(self, pageName, dataBase):
        # Parameter Setup
        self.page_id = None
        self.revision = None
        self.summary = None
        self.rawLinks = None
        self.pageStr = None
        # Init
        wikiName = pageName
        self.pageFetch(pageName, dataBase)
        self.linkDict = self.buildDict()

    # Creates page from database or internet
    def pageFetch(self, pageN, dataBase):
        if dataBase != None:
            self.dbFetch(pageN, dataBase)
        if self.page_id == None:
            self.onlineFetch(pageN, dataBase)

    # Checks if page is in dictionary. If it is, builds page and name within
    # page object. If doesnt exist, it keeps page_id as none
    def dbFetch(self, pageN, dataBase):
        # Setup
        testStr = pageN
        # Database Search
        cursor = dataBase.wikiPages.find({"name":testStr})
        for doc in cursor:
            if doc["name"] == testStr:
                # Builds Page Objects
                self.pageStr = testStr
                self.page_id = doc["page_id"]
                wikiOut = doc["wikipedia"]
                self.revision = wikiOut["revision"]
                self.summary = wikiOut["summary"]
                self.rawLinks = wikiOut["rawLinks"]
                #Builds SuperLinks

                break

    # Fetches page from Wikipedia API
    def onlineFetch(self, pageN, dataBase):
        wikiName = pageN
        # Checks and attmpts to avoid disambiguation errors
        # If the page results in a disambiguation page, each disambiguation
        # option is tried (first to last) to see if actual pages exist
        # goes with first avaliable page.
        try:
            newPage = wikipedia.page(wikiName)
        except wikipedia.exceptions.DisambiguationError as obj:
            possibleOptions = obj.options
            while True:
                if len(possibleOptions) == 0:
                    print "No Good Page Found"
                    quit()
                wikiName = possibleOptions.pop(0)
                if dataBase != None:
                    self.dbFetch(wikiName, dataBase)
                    if self.page_id != None:
                        break
                try:

                    newPage = wikipedia.page(wikiName)
                    break
                except wikipedia.exceptions.DisambiguationError:
                    newNum = 0

        # Updates page name to ensure saved name is the same as the page
        if self.page_id == None:
            self.pageStr = wikiName
            self.page_id = newPage.pageid
            self.revision = newPage.revision_id
            self.summary = newPage.summary
            self.rawLinks = newPage.links
            # Adds new page to DB if DB is passed
            if dataBase != None:
                resultOut = dataBase.wikiPages.insert_one(self.jsonOut())

    # Builds dictionary of None objects based on link names
    def buildDict(self):
        tempArr = self.rawLinks
        lens = len(tempArr)
        newDct = {}

        for i in range(0,lens):
            dictKey = tempArr[i].encode("utf-8")
            newDct[dictKey] = None
        return newDct

    # Pre-populates path with phermones based on historical shortest path
    # Intended only for first setup between start and end goal
    def firstSetup(self, colony, endString, timeStep, reset, dataBase):
        # Parameters
        pherSet = colony.getSetupPherSettings()
        phermoneDropMaxSet = pherSet[0]
        phermoneChangeSet = pherSet[1]

        # Checks if database and historical path exist. If either do not, return
        if dataBase == None:
            return
        docNew = dataBase.wikiLinks.find_one({"startLink":self.pageStr,"endLink":endString})
        if docNew == None:
            return

        pathCount = 0

        for key in docNew["path"]:
            pathCount += 1
            phermoneDropMax = phermoneDropMaxSet
            phermoneChange = phermoneChangeSet
            # Setup Arrays
            checkPath = docNew["path"][key]
            pherPath = []
            # Prepare First Item
            startLoc = checkPath.pop(0)
            pherPath.append(startLoc)
            # Loop to check for links
            while len(checkPath) > 1:
                searchLink = dataBase.wikiLinks.find_one({"startLink":checkPath[0],"endLink":endString})
                if searchLink != None:
                    if searchLink["pathLength"] < len(checkPath):
                        checkPath = searchLink["path"]
                testStr = checkPath.pop(0)
                pherPath.append(testStr)

            endLoc = checkPath.pop(0)
            pherPath.append(endLoc)
            # Build First Link
            self.buildLink(pherPath[1], colony, dataBase)
            # Build Rest of Links
            for nextB in range(1, len(pherPath)-1):
                buildPage = colony.getPage(pherPath[nextB])
                buildPage.buildLink(pherPath[nextB+1],colony,dataBase)
            # Drop Phermones
            for backB in range(2, len(pherPath)+1):
                changePage = colony.getPage(pherPath[-backB])
                if changePage != None:
                    changePage.changePherValue(pherPath[-backB+1], phermoneDropMax, timeStep, reset)
                phermoneDropMax -= phermoneChange
                if phermoneDropMax < 0:
                    phermoneDropMax = 0

        colony.setPathHist(pathCount)

    # Builds Link object between 2 page objects
    def buildLink(self, linkStr, colony, dataBase):
        if self.linkDict[linkStr] == None:
            newLink = PathLink(self, linkStr, colony, dataBase)
            checkStr = newLink.getEndStr()

            # Added to catch disambiguation issues.
            # If page to link has different name than actual page,
            # actual page name is subsituted and passed back
            if checkStr == linkStr:
                self.linkDict[linkStr] = newLink
                return linkStr
            else:
                self.linkDict[checkStr] = newLink
                return checkStr
        else:
            return linkStr

    # Returns name of page as String
    def getPageName(self):
        return self.pageStr

    # Returns random link
    def randLink(self):
        num = len(self.linkDict)
        return self.linkDict.keys()[random.randint(0,num-1)]

    # Returns Link Obj for given link str
    def getLink(self, linkStr):
        return self.linkDict[linkStr]

    # Returns phermone value from linked object
    def linkPherValue(self, linkStr):
        if self.linkDict[linkStr] == None:
            return 0
        else:
            return self.linkDict[linkStr].phermones

    # Return array of links sorted by phermone value. Highest to Lowest Values
    def sortLinks(self, curTime, lastStep):
        sortKeys = []
        valArr = []

        # Update Phermone Values before sorting
        for testKeys, linkObj in self.linkDict.items():
            if not(linkObj == None):
                linkObj.phermoneUpdate(curTime)

        strKeys = self.linkDict.keys()
        keyNum = len(strKeys)-1

        valArr.append(self.linkPherValue(strKeys[keyNum]))
        sortKeys.append(strKeys.pop())

        # Builds Array of Lowest to Highest Phermone Values
        for i in range(0, keyNum):
            counter = 0
            temp = strKeys.pop()

            # Checks to make sure each link is not the same as previous
            # page visited.
            if temp != lastStep:
                tempVal = self.linkPherValue(temp)
                while counter < len(valArr) and tempVal > valArr[counter]:
                    counter = counter + 1
                valArr.insert(counter, tempVal)
                sortKeys.insert(counter, temp)

        # If the top values have the same phermone value, they will be randomly mixed
        if len(valArr) > 1:
            endCheck = valArr[-1]
            penCheck = valArr[-2]
            randMix = []
            while endCheck == penCheck and endCheck != 0 and len(valArr) > 1:
                randMix.append(sortKeys.pop())
                valArr.pop()
                endCheck = valArr[-1]
                penCheck = valArr[-2]

            if len(randMix) > 0:
                randMix.append(sortKeys.pop())
                valArr.pop()
                random.shuffle(randMix)
                sortKeys = sortKeys + randMix

        # Returns REVERSED Array (Higest to Lowest Phermone Values)
        return sortKeys[::-1]

    # Check if topic is a link of current object
    def isLinked(self, linkStr):
        return linkStr in self.linkDict

    # Sets value in link dictionary to provided value
    def setLink(self, linkStr, linkObj = None):
        self.linkDict[linkStr] = linkObj

    # Modify phermone value for specific link
    def changePherValue(self, linkStr, val, timeStep, reset):
        self.linkDict[linkStr].addPhermones(val, timeStep, reset)

    # Creates JSON version of class (for mongoDB Database)
    def jsonOut(self):
        jsonDict = {}
        # jsString = '{'

        # Overview Info
        jsonDict['name'] = self.pageStr
        jsonDict['page_id'] = self.page_id

        # Data from Wikipedia Page object
        jsonWikiDict = {}
        jsonWikiDict['revision'] = self.revision
        jsonWikiDict['summary'] = self.summary
        jsonWikiDict['rawLinks'] = self.rawLinks

        jsonDict['wikipedia'] = jsonWikiDict

        # Data from Link Dictionary
        jsonLinkDict = {}

        jsonDict['links'] = jsonLinkDict

        return jsonDict

class PathLink:
    def __init__(self, startObj, endString, colony, dataBase):
        # Default Parameters
        self.phermones = 0
        self.startStr = startObj.pageStr
        self.endStr = endString
        self.lastUpdate = 0
        self.resetS = 0
        self.evapRate = colony.getEvapRate()
        # Create Links
        endPage = colony.getPage(endString)
        if endPage != None:
            endPage.setLink(self.startStr, self)
        else:
            newPage = PageClass(endString, dataBase)
            newPage.setLink(self.startStr,self)
            colony.addPage(newPage)
            self.endStr = newPage.getPageName()

    # Returns string name of end page
    def getEndStr(self):
        return self.endStr

    # Returns phermones of link
    def getPhermones(self):
        return self.phermones

    # Modifies phermone value of path.
    # Will add the phermone value for current excursion, and degrade current
    # links based on time since update
    def addPhermones(self, val, timeStep, reset):
        if reset != self.resetS:
            self.phermones = 0
            self.resetS = reset
        self.phermoneUpdate(timeStep)
        self.phermones = self.phermones + val

    # Degrades phermone value based on time since last update
    def phermoneUpdate(self, timeStep):
        diff = timeStep - self.lastUpdate
        if self.evapRate >= 1:
            evap = diff*self.evapRate
            self.phermones = self.phermones - evap
        else:
            evap = pow(self.evapRate, diff)
            self.phermones = int(self.phermones*evap)
        self.lastUpdate = timeStep
        if self.phermones < 0:
            self.phermones = 0

    # JSON Generation (for link database)
    def jsonOut(self):
        jsonDict = {}

        # General information
        idStr = (self.startStr + self.endStr).replace(" ", "")
        jsonDict['link_id'] = idStr
        jsonDict['links'] = [self.startStr, self.endStr]

        # Phermone Data
        jsonPherDict = {}

        jsonDict['phermones'] = jsonPherDict

        return jsonDict


class AntMem:

    def __init__(self, startStr, goalStr, life, setArr):
        # Parameter Setup
        self.current = startStr
        self.goal = goalStr
        self.remainingLife = life
        # Phermone Drop Settings
        self.phermoneStart = setArr[0]
        self.phermoneDisp = setArr[1]
        # Random Path Walk Settings
        self.fullChance = setArr[2]
        self.randChance = setArr[3]
        self.secPerc = setArr[4]
        # Initialization
        self.pherMoneDrop = self.phermoneStart
        self.backTrack = False
        self.path = [startStr]
        self.pathCopy = []
        self.contradiction = False
        self.dead = False

    # Checks if ant is dead
    def isDead(self):
        return self.dead

    # Changes ammount of phermone for ant to drop
    # Currently testing halfing drop every time
    def updateDrop(self):
        if self.phermoneDisp >= 1:
            self.pherMoneDrop = self.pherMoneDrop - self.phermoneDisp
        else:
            self.pherMoneDrop = int(self.pherMoneDrop*self.phermoneDisp)
        if self.pherMoneDrop < 0:
            self.pherMoneDrop = 0

    # Moves ant forward along path - main logic
    def move(self, colony, timeStep, reset, dataBase = None):
        if self.backTrack:
            if len(self.path) == 0:
                self.dead = True
            else:
                next = self.path.pop()
                if self.current == next:
                    next = self.path.pop()

                # If in a contradiction (page referenced in path does not actually exist)
                # a phermone update does not occur (the page does not actually have
                # percieved phermone value). Contradiction flag is switched.
                if self.contradiction:
                    self.contradiction = False
                else:
                    pherPage = colony.getPage(self.current)
                    if pherPage != None:
                        pherPage.changePherValue(next, self.pherMoneDrop, timeStep, reset)

                self.updateDrop()
                self.current = next
        else:
            pageC = colony.getPage(self.current)
            if pageC.isLinked(self.goal):
                nextStep = self.goal
                self.backTrack = True
                self.pathCopy = list(self.path)
                self.pathCopy.append(self.goal)

            else:
                if len(self.path) > 1:
                    lastStep = self.path[-2]
                else:
                    lastStep = ""
                posLinks = pageC.sortLinks(timeStep, lastStep)
                if len(posLinks) > 1:
                    testPher = pageC.linkPherValue(posLinks[0])
                    testPher2 = pageC.linkPherValue(posLinks[1])
                    ranInt = random.randint(0,self.fullChance-1)
                    nextStep = None

                    # If random is in random range or no phermones, choose a random link
                    # If random is in range of 2nd percent - go with 2nd best
                    # Else go with best phermone
                    if ranInt < self.randChance or testPher == 0:
                        randPlace = random.randint(0, len(posLinks)-1)
                        nextStep = posLinks[randPlace]
                    elif ranInt < (self.randChance + self.secPerc) and not(testPher2 == 0):
                        nextStep = posLinks[1]
                    else:
                        nextStep = posLinks[0]
                else:
                    nextStep = posLinks[0]

                self.remainingLife = self.remainingLife - 1
                if self.remainingLife < 0:
                    self.dead = True

            errorCheck = False
            # Create New Page for next step
            # If page error, choose another random link as next step
            while True:
                currentP = colony.getPage(self.current)
                try:
                    nextStep = currentP.buildLink(nextStep, colony, dataBase)
                    break
                except wikipedia.exceptions.PageError:
                    print "PAGE ERROR CATCH"
                    errorCheck = True
                    nextStep = currentP.randLink()

            # What happens if goal or element in path does not exist
                # Contradiction - another page will be accessed in path instead,
                # but maybe no phermones should be dropped there?
            if self.backTrack and errorCheck:
                 self.contradiction = True

            self.path.append(nextStep)
            self.current = nextStep


    # Performs ant post mortem
    # Prints path and phermone values if successful
    def postMortem(self, colony, dataBase = None, csvFile = None):
        pathL = 0
        if self.remainingLife < 0:
            print "Died of Natural Causes"
        else:
            print self.pathCopy
            pathL = len(self.pathCopy)
            for n in range(0, pathL-1):
                startStr = self.pathCopy[n]
                endStr = self.pathCopy[n+1]
                pageCheck = colony.getPage(startStr)
                linkObj = pageCheck.getLink(endStr)
                linkPher = linkObj.getPhermones()
                print startStr + " -> (" + str(linkPher) + ") -> " + endStr

            if dataBase != None:
                #Builds SuperLink
                for linkTo in range(1, len(self.pathCopy)):
                    for linkFrom in range(linkTo+1, len(self.pathCopy)+1):
                        # Create Superlink from pathCopy[-linkFrom] to pathCopy[-linkTo]
                        cStart = self.pathCopy[-linkFrom]
                        cEnd = self.pathCopy[-linkTo]
                        if linkTo == 1:
                            pathPart = self.pathCopy[-linkFrom:]
                        else:
                            pathPart = self.pathCopy[-linkFrom:-linkTo+1]
                        superLinkBuild(cStart, cEnd, pathPart, dataBase)
        # Saves data about ant to CSV file
        if csvFile != None:
            dateA = [str(datetime.now())]
            pathSuc = [pathL]
            rowOut = dateA + [colony.getColonySize()] + colony.getSetupPherSettings() + [colony.getEvapRate()] + colony.getAntSetupSettings() + [colony.getPathHist()] + pathSuc
            with open(csvFile, 'ab') as f:
                writer = csv.writer(f)
                writer.writerow(rowOut)

        print "-"
        print "-"


#### ------------------ Non Class Methods
def superLinkBuild(startStr, endStr, path, dataBase):
    # Checks if link exists, and if new link is faster
    # If faster update link (do not have to update page reference to link)
    # If does not exist, create new database link and link page to database link
    pathLen = len(path)
    docNew = dataBase.wikiLinks.find_one({"startLink":startStr,"endLink":endStr})
    # If Link does not exist, new one is made
    if docNew == None:
        newDict = {}
        idStr = (startStr + endStr).replace(" ", "")
        newDict['link_id'] = idStr
        newDict['startLink'] = startStr
        newDict['endLink'] = endStr
        pathDict = {}
        pathDict['Path_0'] = path
        newDict['path'] = pathDict
        newDict['pathLength'] = pathLen
        resultOut = dataBase.wikiLinks.insert_one(newDict)

    else:
        # If new link is shorter, replace existing links
        if pathLen < docNew['pathLength']:
            idCheck = docNew['link_id']
            pathDict = {}
            pathDict['Path_0'] = path
            result = dataBase.wikiLinks.update_one(
                {"link_id":idCheck},
                {"$set": {"pathLength":pathLen,"path":pathDict}})
        # If new link is the same length, add to path as another option
        elif pathLen == docNew['pathLength']:
            idCheck = docNew['link_id']
            pathIn = False
            counter = 1
            for key in docNew['path']:
                counter += 1
                if docNew['path'][key] == path:
                    pathIn = True
            if not(pathIn):
                pathDict = docNew['path']
                nName = "Path_" + str(counter)
                pathDict[nName] = path
                result = dataBase.wikiLinks.update_one(
                    {"link_id":idCheck},
                    {"$set": {"pathLength":pathLen,"path":pathDict}})
