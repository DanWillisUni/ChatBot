import random

import PartTwo.SPHelper as sph
import appSettings

def simResult(fromStation,toStation,delay):
    frequencies = sph.getLatenessFromStations(appSettings.getConnStr(), fromStation,toStation, delay, delay)
    if len(frequencies) > 0:
        sum = 0;
        for i in frequencies:
            sum += int((i.split(",")[1]))
        randIndex = random.randint(0, sum + 1)
        for i in frequencies:
            randIndex -= int((i.split(",")[1]))
            if randIndex < 0:
                return int((i.split(",")[0]))
    return delay