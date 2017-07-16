from classes import AntColony, PageClass, PathLink, AntMem
from pymongo import MongoClient
import random

# -------- DATABASE SETUP
client = MongoClient()
db = client.dexterSwarm

# --------------PARAMETERS
#startPoint = "Malcolm Gladwell"
#endGoal = "Microsoft"
startPoint = "Malcolm Gladwell"
endGoal = "Microsoft"
csvFile = 'rawData.csv'
max_steps = 14
max_ants = 500
concurrent = 4

# --------------INITIALIZATION
#newColony = AntColony(startPoint, endGoal, max_steps, max_ants, concurrent, db, csvFile)

# --------------RUN
#newColony.run()

# -------------- CREATE AND RUN MULTIPLE
moreCol = 1


# CSV Cols
# [Ants in Colony, Ant Life, Setup Max Phermone Drop, Setup Phermone Change, Phermone Evap Rate, Ant Max Phermone Drop, Ant Phermone Change, Random Full Chance, Random Chance, Random Two Chance, Number of Current Historical Options, Resulting Path Length]


for colC in range(0, moreCol):
    newNewCol = AntColony(startPoint, endGoal, max_steps, max_ants, concurrent, db, csvFile)
    newNewCol.run()
    print '------------------------------'
    print str(colC+1) + '/' + str(moreCol)
    print '------------------------------'
