import random

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
        self.pherMoneDrop = self.pherMoneDrop - phermoneDisp
        if self.pherMoneDrop < 0:
            self.pherMoneDrop = 0

    def move(self, pageList, timeStep):
        if self.backTrack:
            next = self.path.pop()
            pageList[self.current].changePherValue(next, self.pherMoneDrop, timeStep)
            self.updateDrop()
            self.current = next
        else:
            if pageList[self.current].isLinked(self.goal):
                nextStep = self.goal
            else:
                posLinks = pageList[self.current].sortLinks()
                testPher = pageList[self.current].linkPherValue(posLinks[0])
                ranInt = random.randint(0,self.fullChance-1)
                nextStep = None
                if ranInt < self.randChance or testPher == 0:
                    randPlace = random.randint(0, len(posLinks)-1)
                    nextStep = posLinks[randPlace]
                elif ranInt < self.firstPerc:
                    nextStep = posLink[0]
                elif ranInt < self.secPerc:
                    nextStep = posLink[1]

            pageList[self.current].buildLink(nextStep, pageList)

            if nextStep == self.goal:
                self.backTrack = True
            self.path.append(nextStep)
            self.current = nextStep
