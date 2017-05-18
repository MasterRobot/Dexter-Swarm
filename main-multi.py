from multiprocessing import Process
import os
from classes import PageClass, PathLink, AntMem
import pickle
import random

def info(title):
    print title
    print 'module name:', __name__
    print 'process id:', os.getpid()

def antTurn(startPoint, endPoint, pageLib, turnTime, resetVal, death):
    gershwin = AntMem(startPoint,endPoint)
    allPages[startPoint] = PageClass(startPoint)

    for k in range(0,death):
        gershwin.move(allPages,currentTime, resetSeed)
        print "Current = ", gershwin.current
        currentTime = currentTime + 1
        if gershwin.current == startPoint:
            print "WIN"
            break

if __name__ == '__main__':
    info('main line')
    

resetSeed = random.randint(0,50000)

allPages = {}
currentTime = 0

pkl_file = open('wikiData.pkl', 'rb')
allPages = pickle.load(pkl_file)
print allPages.keys()
print len(allPages.keys())
pkl_file.close()



startPoint = "Malcolm Gladwell"
endGoal = "Microsoft"

antTurn(startPoint, endGoal, allPages, currentTime, resetVal, 30)

output = open('wikiData.pkl', 'wb')
pickle.dump(allPages, output)
