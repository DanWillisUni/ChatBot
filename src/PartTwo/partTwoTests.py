import ProbabilityHelpers as ph

connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;"
#connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Charlies
#connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Brandons

allLate = ph.getLatenessFrequencies(connStr,"SOTON","WATRLMN",2)
totalFrequency = 0
sum = 0.0
for l in allLate:
    totalFrequency += int((l.split(",")[1]))
for l in allLate:
    sum += float(int(l.split(",")[0]) * int(l.split(",")[1]) / totalFrequency)
print(sum)
