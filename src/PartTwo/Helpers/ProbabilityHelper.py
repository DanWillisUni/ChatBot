import math
import copy

def probFromFrequency(f,min):
    totalFrequency = 0
    totalLate = 0
    for l in f:
        totalFrequency += int((l.split(",")[1]))
        if int((l.split(",")[0])) >= min:
            totalLate += int((l.split(",")[1]))
    return float(totalLate / totalFrequency)

def getQ(arr,qMultiplyer):
    arr.sort()
    l = len(arr)
    firstIndex = l * qMultiplyer
    if firstIndex % 1 == 0:
        return arr[int(firstIndex)]
    elif firstIndex % 1 == 0.5:
        return (arr[math.floor(firstIndex)] + arr[math.ceil(firstIndex)])/2
    else:
        return arr[round(firstIndex)]

def getIQR(arr):
    arr.sort()
    q1 = getQ(arr,0.25)
    q3 = getQ(arr,0.75)
    return q3-q1

def getOutliersIndex(arr):
    arr.sort()
    q1 = getQ(arr, 0.25)
    q3 = getQ(arr, 0.75)
    iqr = q3-q1
    return (q3+(1.5*iqr))