import wikipedia
import random


class PageClass:
    def __init__(self,pageName):
        self.pageStr = pageName
        self.page = wikipedia.page(pageName)
        self.linkDict = self.buildDict()

    def buildDict(self):
        tempArr = self.page.links
        lens = len(tempArr)
        newDct = {}

        for i in range(0,lens):
            dictKey = tempArr[i].encode("utf-8")
            newDct[dictKey] = None
        return newDct

    def isLinked(self, linkStr):
        return linkStr in self.linkDict

    def addLink(self, linkStr):
        # Adds link place into dictionary
        self.linkDict[linkStr] = None

    def randLink(self):
        num = len(self.linkDict)
        return self.linkDict.keys()[random.randint(0,num-1)]

    def buildLink(self, linkStr, fullDict):
        # Builds Link object between 2 page objects
        if self.linkDict[linkStr] == None:
            self.linkDict[linkStr] = PathLink(self,linkStr, fullDict)

    def setLink(self, linkStr, linkObj):
        self.linkDict[linkStr] = linkObj

    def linkPherValue(self, linkStr):
        if self.linkDict[linkStr] == None:
            return 0
        else:
            return self.linkDict[linkStr].phermones

    def changePherValue(self, linkStr, val, timeStep, reset):
        self.linkDict[linkStr].addPhermones(val, timeStep, reset)

    def sortLinks(self):
        sortKeys = []
        valArr = []
        strKeys = self.linkDict.keys()
        keyNum = len(strKeys)-1

        valArr.append(self.linkPherValue(strKeys[keyNum]))
        sortKeys.append(strKeys.pop())

        for i in range(0, keyNum):
            counter = 0
            temp = strKeys.pop()
            tempVal = self.linkPherValue(temp)
            while counter < len(valArr) and tempVal > valArr[counter]:
                counter = counter + 1
            valArr.insert(counter, tempVal)
            sortKeys.insert(counter, temp)

        return sortKeys[::-1]


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
            newPage.setLink(self.startStr,self)
            fullDict[endString] = newPage

    def addPhermones(self, val, timeStep, reset):
        if reset != self.resetS:
            self.phermones = 0
            self.resetS = reset
        self.phermoneUpdate(timeStep)
        self.phermones = self.phermones + val

    def phermoneUpdate(self, timeStep):
        diff = timeStep - self.lastUpdate
        evap = diff*self.evapRate
        self.phermones = self.phermones - evap
        self.lastUpdate = timeStep
        if self.phermones < 0:
            self.phermones = 0


class AntMem:

    phermoneStart = 100
    phermoneDisp = 5

    fullChance = 10
    randChance = 1
    firstPerc = 7
    secPerc = 10


    def __init__(self, startStr, goalStr):
        self.current = startStr
        self.goal = goalStr
        self.pherMoneDrop = self.phermoneStart
        self.backTrack = False
        self.path = [startStr]

    def updateDrop(self):
        self.pherMoneDrop = self.pherMoneDrop - self.phermoneDisp
        if self.pherMoneDrop < 0:
            self.pherMoneDrop = 0

    def move(self, pageList, timeStep, reset):
        if self.backTrack:
            next = self.path.pop()
            if self.current == next:
                next = self.path.pop()
            pageList[self.current].changePherValue(next, self.pherMoneDrop, timeStep, reset)
            self.updateDrop()
            self.current = next
        else:
            if pageList[self.current].isLinked(self.goal):
                nextStep = self.goal
                print "GOAL"
            else:
                posLinks = pageList[self.current].sortLinks()
                testPher = pageList[self.current].linkPherValue(posLinks[0])
                ranInt = random.randint(0,self.fullChance-1)
                nextStep = None
                if ranInt < self.randChance or testPher == 0:
                    randPlace = random.randint(0, len(posLinks)-1)
                    nextStep = posLinks[randPlace]
                elif ranInt < self.firstPerc:
                    nextStep = posLinks[0]
                elif ranInt < self.secPerc:
                    nextStep = posLinks[1]

            while True:
                try:
                    pageList[self.current].buildLink(nextStep, pageList)
                    break
                except wikipedia.exceptions.PageError:
                    print "CATCH"
                    nextStep = pageList[self.current].randLink()

            if nextStep == self.goal:
                self.backTrack = True
            self.path.append(nextStep)
            self.current = nextStep
