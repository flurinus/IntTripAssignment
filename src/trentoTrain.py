
class TrentoTrain(object):
    '''
    Object representing main information from NS' TRENTO train database. Required only for reading data.
    '''

    def __init__(self, platformSequence, stationNameSequence, arrTimeSched, depTimeSched, arrTimeReal, depTimeReal,
                 rollingStockType, numCars, carSeatCap, trainLength):
        self.platformSequence = platformSequence
        self.stationNameSequence = stationNameSequence
        self.arrTimeSched = arrTimeSched
        self.depTimeSched = depTimeSched
        self.arrTimeReal = arrTimeReal
        self.depTimeReal = depTimeReal
        self.rollingStockType = rollingStockType
        self.numCars = numCars
        self.carSeatCap = carSeatCap
        self.trainLength = trainLength
        
        # consistency check
        numStops = len(platformSequence)
        assert( len(self.arrTimeSched) == numStops and len(self.depTimeSched) == numStops and 
                len(self.arrTimeReal) == numStops and len(self.depTimeReal) == numStops)
        
        #stops are chronologically ordered
        for stopNum in range(0,numStops-1):
            assert(self.arrTimeSched[stopNum] < self.arrTimeSched[stopNum+1])
            assert(self.arrTimeReal[stopNum] < self.arrTimeReal[stopNum+1]) 
        
            assert(self.depTimeSched[stopNum] < self.depTimeSched[stopNum+1]), "stopNum: %d, depTime: %s < %s" % (stopNum, self.depTimeSched[stopNum],self.depTimeSched[stopNum+1])
            assert(self.depTimeReal[stopNum] < self.depTimeReal[stopNum+1])
            
        #arrivals occur before departures, and trains do not depart run early (may be relaxed)
        for stopNum in range(0,numStops):
            assert(self.arrTimeSched[stopNum] < self.depTimeSched[stopNum])
            assert(self.arrTimeReal[stopNum] < self.depTimeReal[stopNum]), \
            "Train must arrive (%s) before it departs (%s)" % (self.arrTimeReal[stopNum], self.depTimeReal[stopNum])
            
            #not strictly required
            #if self.depTimeReal[stopNum] < self.depTimeSched[stopNum] and Parameter.showWarnings:
            #    print("Train departing early by %ss on platform %s (realized: %s, scheduled: %s)" %\
            #          (self.depTimeSched[stopNum]-self.depTimeReal[stopNum], platformSequence[stopNum], \
            #           self.depTimeReal[stopNum], self.depTimeSched[stopNum]) ) 
            
        #train length, car capacity and number of cars strictly positive_address
        assert( self.numCars > 0 and self.carSeatCap > 0 and self.trainLength > 0 )
    
    def __repr__(self):
        
        tStr = "%s, " % self.platformSequence
        #tStr += "stationNameSequence: %s, " % self.stationNameSequence
        tStr += "arrTimeReal: %s, " % self.arrTimeReal
        tStr += "depTimeReal: %s, " % self.depTimeReal
        #tStr += "arrTimeSched: %s, " % self.arrTimeSched
        #tStr += "depTimeSched: %s, " % self.depTimeSched 
        tStr += "trainLength: %s m" % self.trainLength
        
        return tStr