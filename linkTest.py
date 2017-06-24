#------------------------------------------------------------
#--------------- Link Test

allPages["Oceans"] = PageClass("Oceans")
allPages["Floating match on card"] = PageClass("Floating match on card")

allPages["Oceans"].buildLink("Floating match on card", allPages)
print allPages.keys()
allPages["Oceans"].changePherValue("Floating match on card", 10)
print "ocean side =", allPages["Oceans"].linkPherValue("Floating match on card")
print "other side =", allPages["Floating match on card"].linkPherValue("Oceans")
print allPages.keys()
