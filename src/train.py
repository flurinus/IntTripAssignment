from vehicle import Vehicle
from parameter import Parameter 
class Train(object):

    def __init__(self, platformSeqRaw, arrTimeRealRaw, depTimeRealRaw, arrTimeSchedRaw, depTimeSchedRaw,\
                rollingStockType, numCars, carSeatCap, length, simEnv, pedNet, param):
        
        self.curPlatform = None
        self.platformNameDict = dict()
        self.platformNameDictRev = dict()
        self.stationNameDict = dict()
        self.stationNameDictRev = dict()
        self.arrTimesReal = dict()
        self.depTimesReal = dict()
        self.arrTimesSched = dict()
        self.depTimesSched = dict()
        
        #add upstream and downstream stations
        assert( len(platformSeqRaw) > 0), "train must serve at least one station"
        
        #copy lists to add up- and downstream nodes
        platformSeq = list(platformSeqRaw)
        arrTimeReal = list(arrTimeRealRaw) 
        arrTimeSched = list(arrTimeSchedRaw)
        depTimeReal = list(depTimeRealRaw)
        depTimeSched = list(depTimeSchedRaw)
        
        #insert upstream station
        platformSeq.insert(0,Parameter.upstreamPlatform)
        arrTimeReal.insert(0, arrTimeRealRaw[0] - Parameter.timeDeltaUpDownTrip - Parameter.dwellTimeUpDownStream)
        arrTimeSched.insert(0, arrTimeSchedRaw[0] - Parameter.timeDeltaUpDownTrip - Parameter.dwellTimeUpDownStream)
        depTimeReal.insert(0, arrTimeRealRaw[0] - Parameter.timeDeltaUpDownTrip)
        depTimeSched.insert(0, arrTimeSchedRaw[0] - Parameter.timeDeltaUpDownTrip)
        
        
        #append downstream station
        platformSeq.append(Parameter.downstreamPlatform)
        arrTimeReal.append(depTimeRealRaw[-1] + Parameter.timeDeltaUpDownTrip)
        arrTimeSched.append(depTimeSchedRaw[-1] + Parameter.timeDeltaUpDownTrip)
        depTimeReal.append(depTimeRealRaw[-1] + Parameter.timeDeltaUpDownTrip + Parameter.dwellTimeUpDownStream)
        depTimeSched.append(depTimeSchedRaw[-1] + Parameter.timeDeltaUpDownTrip + Parameter.dwellTimeUpDownStream)
        
        self.numStops = len(platformSeq)
        assert(len(platformSeq) == len(arrTimeReal) == len(depTimeReal) == len(arrTimeSched) == len(depTimeSched))
        
        
        self.arrivalEvent = dict()
        self.departureEvent = dict()
        
        assert(rollingStockType in Parameter.boardAlightServiceTimesPerVehicle.keys()), \
            "rollingStockType %s not found in rolling stock catalogue (%s)" % \
            (rollingStockType, Parameter.boardAlightServiceTimesPerVehicle.keys() )
            
        self.rollingStockType = rollingStockType
        assert(numCars > 0 and ( isinstance(numCars,int) or numCars.is_integer() ) ), "numCars: %s" % numCars
        self.numVehicles = int( numCars )
        self.vehSeatCap = carSeatCap
        
        #train length
        self.length = length
        assert(self.length > 0), "length: %s" % self.length

        for stopNumber in range(0,self.numStops):
            platformName = platformSeq[stopNumber]
            self.platformNameDict[stopNumber] = platformName
            
            #train should stop at most once at a platform
            assert(platformName not in self.platformNameDictRev), \
                "platform %s appearing multiple times in platform sequence: %s" % (platformName, platformSeq) 
            self.platformNameDictRev[platformName] = stopNumber 
            
            self.arrTimesReal[stopNumber]  = arrTimeReal[stopNumber]
            self.depTimesReal[stopNumber]  = depTimeReal[stopNumber]
            
            self.arrTimesSched[stopNumber]  = arrTimeSched[stopNumber]
            self.depTimesSched[stopNumber]  = depTimeSched[stopNumber]
            
            self.arrivalEvent[stopNumber] = simEnv.event()
            self.departureEvent[stopNumber] = simEnv.event()
            
            stationName = pedNet.platformStationDict[platformName]
            self.stationNameDict[stopNumber] = stationName
            self.stationNameDictRev[stationName] = stopNumber
        
        self.vehicleDict = dict()
            
        for vehNumber in range(0,self.numVehicles):
            self.vehicleDict[vehNumber] = Vehicle(carSeatCap, rollingStockType, simEnv)
            
        self.logBook = list()
        
        self.param = param
                
    def getArrivalEvent(self, platformName):
        stopNumber = self.platformNameDictRev[platformName]
        return self.arrivalEvent[stopNumber]
    
    def getDepartureEvent(self, platformName):
        stopNumber = self.platformNameDictRev[platformName]
        return self.departureEvent[stopNumber]
    
    def getPlatform(self, stationName, pedNet):        
        station = pedNet.stationDict[stationName]
        stationPlatforms = station.platformNameSet
        
        trainPlatforms = set(self.platformNameDict.values())
        
        commonPlatform = stationPlatforms & trainPlatforms
        
        #train and station have one platform in common
        assert(1==len(commonPlatform)), \
            "stationPlatforms: %s, trainPlatforms: %s, commonPlatforms: %s (should be one)" %\
            (stationPlatforms, trainPlatforms, commonPlatform)
        
        return next(iter(commonPlatform))
    
    def getDepTimeForPlatform(self, platformName):
        if platformName not in self.platformNameDictRev.keys():
            print("Cannot find %s in platformNameDictRev: %s" % (platformName,self.platformNameDictRev))
            return False
        else:
            stopNumber = self.platformNameDictRev[platformName]
            return self.depTimesReal[stopNumber]
    
    def getDepTimeforStation(self,stationName):
        if (stationName in self.stationNameDictRev):
            stopNumber = self.stationNameDictRev[stationName]
            return self.depTimesReal[stopNumber]
        else:
            return False
    
    def getArrTimeforStation(self,stationName):
        if (stationName in self.stationNameDictRev):
            stopNumber = self.stationNameDictRev[stationName]
            return self.arrTimesReal[stopNumber]
        else:
            return False
    
                
    def propagate(self, simEnv, pedNet):
        
        for stopNumber in range(0,self.numStops):
            
            curArrTime = self.arrTimesReal[stopNumber]
            curDepTime = self.depTimesReal[stopNumber]
            
            if (curArrTime < simEnv.now):
                
                delayStr = "Late arrival by %.1f s at %s (%s), had arrived at %.1f (actual observation: %.1f) and departure according observation scheduled at %.1f"\
                    % (simEnv.now-curArrTime, self.platformNameDict[stopNumber], self.stationNameDict[stopNumber], \
                       simEnv.now, curArrTime, curDepTime)
                    
                delayStr += "\n%s" % (''.join('{%.1f}: {%s}\n' %  (time,entry)  for (time,entry) in self.logBook))
                
                print(delayStr)
                
                curArrTime = simEnv.now
            
            #arrive
            yield simEnv.timeout(curArrTime - simEnv.now)
            self.curPlatform = self.platformNameDict[stopNumber]
            self.arrivalEvent[stopNumber].succeed()
            
            if Parameter.textOutput or self.param.isFinalInstance:
                self.logEntry(simEnv, pedNet)
            
            #depart
            #wait for departure time
            if (curDepTime < simEnv.now):
                
                delayStr = "Late departure by %.1f s at %s (%s), had arrived at %.1f (actual observation: %.1f) and departs at %.1f (actual observation: %.1f)"\
                    % (simEnv.now-curDepTime, self.platformNameDict[stopNumber], self.stationNameDict[stopNumber], \
                       curArrTime, self.arrTimesReal[stopNumber], simEnv.now, curDepTime)
                    
                delayStr += "\n%s" % (''.join('{%.1f}: {%s}\n' %  (time,entry)  for (time,entry) in self.logBook))
                
                print(delayStr)
                
                curDepTime = simEnv.now
            
            
            yield simEnv.timeout(curDepTime - simEnv.now)
            
            #no remaining alighting or boarding passengers in any vehicle
            for vehicle in self.vehicleDict.values():
                #send boarding passenger with low priority and zero boarding time
                with vehicle.door.request(priority=10) as lastBoardReq:
                    yield lastBoardReq
            
            self.curPlatform = None
            self.departureEvent[stopNumber].succeed()
            
            if (simEnv.now-curDepTime) > 30:
                #May occur only occasionally, otherwise door capacity may be set too low.
                print("Uncompensated train delay of %.1f" % (simEnv.now-curDepTime))
            
            if Parameter.textOutput or self.param.isFinalInstance:
                self.logEntry(simEnv, pedNet)
            
    def getRidership(self):
        ridership = 0
        
        for vehicle in self.vehicleDict.values():
            ridership += vehicle.cabin.passengerLoad
            
        return ridership
            
    def logEntry(self, simEnv, pedNet):
        logTime = simEnv.now
        
        if self.curPlatform is not None:
            logEntry = "on platform %s, ridership: %d" % (self.curPlatform, self.getRidership())
            
            #update car-specific ridership log book
            stationName = pedNet.platformStationDict[self.curPlatform]
            
            #for each vehicle separately, store ridership at arrival
            for vehicle in self.vehicleDict.values():
                vehicle.logRidershipAtArrival(stationName)
                
        else:
            logEntry = "departed, ridership: %d" % self.getRidership()
            
        self.logBook.append([logTime,logEntry])