def probFromFrequency(f,min):
    totalFrequency = 0
    totalLate = 0
    for l in f:
        totalFrequency += int((l.split(",")[1]))
        if int((l.split(",")[0])) >= min:
            totalLate += int((l.split(",")[1]))
    return float(totalLate / totalFrequency)