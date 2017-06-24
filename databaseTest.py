from classes import PageClass, PathLink, AntMem
from pymongo import MongoClient

# Using "Waiakea" and "Hilo Bay"

# Connect to DB
# Name of DB is Dexter-Swarm
# has collections "wikiLinks" and "wikiPages"
client = MongoClient()
db = client.dexterSwarm

# Create Objects
pageA = PageClass("Waiakea")
pageB = PageClass("Hilo Bay")
pageA.buildSimpleLink(pageB)
linkAB = pageA.getLink("Hilo Bay")

# Add Objects to DB
resultA = db.wikiPages.insert_one(pageA.jsonOut())
print(resultA)
resultB = db.wikiPages.insert_one(pageB.jsonOut())
print(resultB)
resultC = db.wikiLinks.insert_one(linkAB.jsonOut())
print(resultC)
