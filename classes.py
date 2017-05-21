import wikipedia
import random
import json

# Class to store information about a specific wikipedia page
# Stored information -
#       - Page name (hopefully topic)
#       - Page object from wikipedia class
#       - Dictionary of links (build from wikipedia class)

class PageClass:
    def __init__(self,pageName):
        wikiName = pageName
        try:
            newPage = wikipedia.page(wikiName)
        except wikipedia.exceptions.DisambiguationError as obj:
            possibleOptions = obj.options
            while True:
                if len(possibleOptions) == 0:
                    print "No Good Page Found"
                    quit()
                wikiName = possibleOptions.pop(0)
                try:
                    newPage = wikipedia.page(wikiName)
                    break
                except wikipedia.exceptions.DisambiguationError:
                    newNum = 0
        self.pageStr = wikiName
        self.page = newPage
        self.linkDict = self.buildDict()

    def getPageName(self):
        return self.pageStr

    def buildDict(self):
        tempArr = self.page.links
        lens = len(tempArr)
        newDct = {}

        for i in range(0,lens):
            dictKey = tempArr[i].encode("utf-8")
            newDct[dictKey] = None
        return newDct

    # Check if topic is a link of current object
    def isLinked(self, linkStr):
        return linkStr in self.linkDict

    # Returns random link
    def randLink(self):
        num = len(self.linkDict)
        return self.linkDict.keys()[random.randint(0,num-1)]

    # Returns phermone value from linked object
    def linkPherValue(self, linkStr):
        if self.linkDict[linkStr] == None:
            return 0
        else:
            return self.linkDict[linkStr].phermones

    # Adds empty link into dictionary
    def addLink(self, linkStr):
        self.linkDict[linkStr] = None

    # Builds Link object between 2 page objects
    def buildLink(self, linkStr, fullDict):
        if self.linkDict[linkStr] == None:
            #self.linkDict[linkStr] = PathLink(self,linkStr, fullDict)
            newLink = PathLink(self, linkStr, fullDict)
            checkStr = newLink.getEndStr()
            if checkStr == linkStr:
                self.linkDict[linkStr] = newLink
                return linkStr
            else:
                self.linkDict[checkStr] = newLink
                return checkStr
        else:
            return linkStr


    # def buildSimpleLink(self, pageObj2Link):
    #     linkStr = pageObj2Link.pageStr
    #     if self.linkDict[linkStr] == None:
    #         self.linkDict[linkStr] = PathLink(self,pageObj2Link)

    # Returns Link Obj for given link str
    def getLink(self, linkStr):
        return self.linkDict[linkStr]

    # Sets value in link dictionary to provided value
    def setLink(self, linkStr, linkObj):
        self.linkDict[linkStr] = linkObj

    # Modify phermone value for specific link
    def changePherValue(self, linkStr, val, timeStep, reset):
        self.linkDict[linkStr].addPhermones(val, timeStep, reset)

    # Return array of links sorted by phermone value. Highest to Lowest Values
    def sortLinks(self, curTime):
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
            tempVal = self.linkPherValue(temp)
            while counter < len(valArr) and tempVal > valArr[counter]:
                counter = counter + 1
            valArr.insert(counter, tempVal)
            sortKeys.insert(counter, temp)

        # Returns REVERSED Array (Higest to Lowest Phermone Values)
        return sortKeys[::-1]

#    def pOut(self):
#        print('Obj Name: ' + self.pageStr)
#        print('Page Name: ' + self.pageStr)

    # Creates JSON version of class (for mongoDB Database)
    def jsonOut(self):
        jsonDict = {}
        # jsString = '{'

        # Overview Info
        jsonDict['name'] = self.pageStr
        jsonDict['page_id'] = self.page.pageid

        # Data from Wikipedia Page object
        jsonWikiDict = {}
        jsonWikiDict['revision'] = self.page.revision_id
        jsonWikiDict['summary'] = self.page.summary
        jsonWikiDict['rawLinks'] = self.page.links

        jsonDict['wikipedia'] = jsonWikiDict

        # Data from Link Dictionary
        #jsString = jsString + '"links": {'
        #jsString = jsString + '}'
        jsonLinkDict = {}

        jsonDict['links'] = jsonLinkDict


        return jsonDict



class PathLink:

    #global allPages
    evapRate = 2

    def __init__(self, startObj, endString, fullDict):
        # Default Parameters
        self.phermones = 0
        self.startStr = startObj.pageStr
        self.endStr = endString
        self.lastUpdate = 0
        self.resetS = 0
        # Create Link
        if endString in fullDict:
            fullDict[endString].setLink(self.startStr, self)
        else:
            newPage = PageClass(endString)
            self.endStr = newPage.getPageName()
            newPage.setLink(self.startStr,self)
            fullDict[self.endStr] = newPage

    # def __init__(self, startObj, endObj):
    #     # Default Parameters
    #     self.phermones = 0
    #     self.startStr = startObj.pageStr
    #     self.endStr = endObj.pageStr
    #     self.lastUpdate = 0
    #     self.resetS = 0
    #     # Create Link
    #     endObj.setLink(self.startStr,self)

    def getEndStr(self):
        return self.endStr

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
        evap = diff*self.evapRate
        self.phermones = self.phermones - evap
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

    phermoneStart = 100
    phermoneDisp = 5

    fullChance = 20
    randChance = 1
    # firstPerc = 7 - replaced with difference
    secPerc = 3


    def __init__(self, startStr, goalStr, life):
        self.current = startStr
        self.goal = goalStr
        self.pherMoneDrop = self.phermoneStart
        self.backTrack = False
        self.path = [startStr]
        self.pathCopy = []
        self.contradiction = False
        self.remainingLife = life
        self.dead = False

    def updateDrop(self):
        self.pherMoneDrop = self.pherMoneDrop - self.phermoneDisp
        if self.pherMoneDrop < 0:
            self.pherMoneDrop = 0

    def isDead(self):
        return self.dead

    def postMortem(self, allPages):
        if self.remainingLife < 0:
            print "Died of Natural Causes"
        else:
            print self.pathCopy

            for n in range(0, len(self.pathCopy)-1):
                startStr = self.pathCopy[n]
                endStr = self.pathCopy[n+1]
                linkObj = allPages[startStr].getLink(endStr)
                linkPher = linkObj.getPhermones()
                print startStr + " -> (" + str(linkPher) + ") -> " + endStr
        print "-"
        print "-"



    def move(self, pageList, timeStep, reset):
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
                    pageList[self.current].changePherValue(next, self.pherMoneDrop, timeStep, reset)

                self.updateDrop()
                self.current = next
        else:
            if pageList[self.current].isLinked(self.goal):
                nextStep = self.goal
                self.backTrack = True
                self.pathCopy = list(self.path)
                self.pathCopy.append(self.goal)

            else:
                posLinks = pageList[self.current].sortLinks(timeStep)
                testPher = pageList[self.current].linkPherValue(posLinks[0])
                testPher2 = pageList[self.current].linkPherValue(posLinks[1])
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

                self.remainingLife = self.remainingLife - 1
                if self.remainingLife < 0:
                    self.dead = True

            errorCheck = False
            # Create New Page for next step
            # If page error, choose another random link as next step
            while True:
                try:
                    nextStep = pageList[self.current].buildLink(nextStep, pageList)
                    break
                except wikipedia.exceptions.PageError:
                    print "PAGE ERROR CATCH"
                    errorCheck = True
                    nextStep = pageList[self.current].randLink()

            # What happens if goal or element in path does not exist
                # Contradiction - another page will be accessed in path instead,
                # but maybe no phermones should be dropped there?
            if self.backTrack and errorCheck:
                 self.contradiction = True

            self.path.append(nextStep)
            self.current = nextStep
