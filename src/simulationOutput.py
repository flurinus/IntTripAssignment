from parameter import Parameter
import statistics


class SimulationOutput(object):

    def __init__(self, pedNet, transSys, travPop, param):
        
        self.param = param
        
        self.computeLinkFlows(pedNet)
        self.computeAreaDensity(pedNet)
        self.computeOccupationOnPlatforms(pedNet)
        self.computeAverageUtilityFractions(travPop, pedNet)
        
        self.consolidateTrainRidership(transSys)
        
    def computeAverageUtilityFractions(self, travPop, pedNet):
        #contains cumulative utility of passengers of all OD relations
        self.connUtilityLog = dict()
        
        for connection in Parameter.plotConnections:
            #initialize utility dict
            utilityDict = {'walking':[], 'waiting':[], 'riding':[]}
            self.connUtilityLog[connection] = utilityDict
        
        #consider observed utilities in their connection dict
        for ped in travPop.pedestrianDict.values():
            
            origAreaName = pedNet.linkIDAreaIDDict[ped.origLinkID]
            origStationName = pedNet.areaStationDict[origAreaName]
            
            destAreaName = pedNet.linkIDAreaIDDict[ped.destLinkID]
            destStationName = pedNet.areaStationDict[destAreaName]
            
            #connection of current pedestrian
            pedConn = (origStationName,destStationName)
            
            #consider only corridor passengers that have not missed a train
            if pedConn in Parameter.plotConnections:
                self.connUtilityLog[pedConn]['walking'].append( ped.totalWalkUtility )
                self.connUtilityLog[pedConn]['waiting'].append( ped.totalWaitUtility )
                self.connUtilityLog[pedConn]['riding'].append( ped.totalRideUtility )
        
        #compute average utilities per connection
        self.avgConnUtility = dict()
        self.stDevConnUtility = dict()
        self.numPassPerConn = dict()
        
        for connection in Parameter.plotConnections:
            #reset number of passengers to force initialization
            numPass = None
            
            #initialize connection-specific utility dict
            self.avgConnUtility[connection] = dict()
            self.stDevConnUtility[connection] = dict()
            
            for activity in {'walking','waiting','riding'}:
                utilityLog = self.connUtilityLog[connection][activity]
                
                if numPass is None:
                    numPass = len(utilityLog)
                    self.numPassPerConn[connection] = numPass
                
                avgUtility = None
                if numPass > 0:
                    avgUtility = sum(utilityLog) / numPass
                    if len(utilityLog) > 1:
                        stDevUtility = statistics.stdev(utilityLog)
                    else:
                        print("Insufficient data to calculate standard deviation for %s, %s" % (connection,activity))
                        stDevUtility=0
                
                    self.avgConnUtility[connection][activity] = avgUtility
                    self.stDevConnUtility[connection][activity] = stDevUtility
                                    
        #print("self.avgConnUtility: %s" % self.avgConnUtility)
        #print("self.stDevConnUtility: %s" % self.stDevConnUtility)
        
            
    def computeOccupationOnPlatforms(self, pedNet):
        
        assert(self.areaDensityDict is not None), "class method self.computeAreaDensity() needs to be executed "
        
        #occupation on all platforms in station
        stationPlatformAreaSet = dict()
        self.stationPlatformOccupationDict = dict()
        
        #for each station initialize set of platform areas
        for stationID in pedNet.stationDict.keys():
            stationPlatformAreaSet[stationID] = set()
            
        #for each station generate set of platform areas
        for boardLinkID, platformID in pedNet.boardingLinkPlatformDict.items():
            areaID = pedNet.linkIDAreaIDDict[boardLinkID]
            stationID = pedNet.platformStationDict[platformID]
            
            stationPlatformAreaSet[stationID].add(areaID)
        
        #compute platform occupation    
        for stationName, areaSet in stationPlatformAreaSet.items():
            #list containing occupation at each time point
            occupList = [0]*Parameter.numTimePointsAnalysis
            
            for areaName in areaSet:
                areaSize = pedNet.areaDict[areaName].resource.areaSize
                
                occupList = [x[0] + x[1]*areaSize \
                    for x in zip(occupList, self.areaDensityDict[areaName] ) ]
                
            self.stationPlatformOccupationDict[stationName] = occupList
            
    def computeAreaDensity(self, pedNet):
        
        self.areaDensityDict = dict()
        
        for areaName, area in pedNet.areaDict.items():
            #cumulative density and number of observations for each data point
            cumDensity = [0] * Parameter.numTimePointsAnalysis
            numObs = [0] * Parameter.numTimePointsAnalysis
            
            #IMPORTANT NOTE: The below method to compute the time-mean density in an area
            #is a proxy. It assumes that observations are time-independent within an analysis window.
            #The error made is probably small, as long as the analysis time intervals are short.
            #If these analysis time intervals are very short (e.g. 10 sec), the error is negligible.
            
            #retrieve density logs and add them to the bins             
            for obsTime, obsDens in area.resource.densityLog.items():
                #consider only observations with relevant time frame
                if self.param.analysisStart <= obsTime and obsTime < self.param.analysisEnd:
                    #find time bin
                    binID = int( (obsTime - self.param.analysisStart) // self.param.timeStepAnalysis )
                    
                    #add density observation and increase counts in bin
                    cumDensity[binID] += obsDens
                    numObs[binID] += 1
            
            #compute density for each time point
            densityPoints = [0] * Parameter.numTimePointsAnalysis
            
            for i in range(0,Parameter.numTimePointsAnalysis):
                if numObs[i] > 0:
                    densityPoints[i] = cumDensity[i]/numObs[i]
                    
            self.areaDensityDict[areaName] = densityPoints    
            
    def computeLinkFlows(self, pedNet):
        
        self.linkFlowRateDict = dict()
        self.linkCumFlowDict = dict()
        
        for streamID, stream in pedNet.streamDict.items():
            #flow at each time point
            flow = [0] * Parameter.numTimePointsAnalysis
            
            #retrieve arrival time logs and add them to the bins             
            for obsTime in stream.arrivalLogBook:
                #consider only observations with relevant time frame
                if self.param.analysisStart <= obsTime and obsTime < self.param.analysisEnd:
                    #find time bin and increase
                    binID = int( (obsTime - self.param.analysisStart) // self.param.timeStepAnalysis )
                    flow[binID] += 1
            
            #compute flow rate (pass/min) and cumulative flow
            flowRate = list()
            cumulativeFlow = list()
            
            totFlow = 0
            
            for i in range(0,Parameter.numTimePointsAnalysis):
                flowRate.append( flow[i]/self.param.timeStepAnalysis*60 )

                totFlow += flow[i]
                cumulativeFlow.append(totFlow)
                
            streamName = pedNet.streamIDDict[streamID]
                    
            self.linkFlowRateDict[streamName] = flowRate
            self.linkCumFlowDict[streamName] = cumulativeFlow

        
    def consolidateTrainRidership(self, transSys):
                    
        #nested dict of the form dict[trainName][vehID]
        #total ridership: all users, tracked: only corridor passengers, auxiliary: users from upstream and/or to downstream
        self.totalRidershipLogDict = dict()
        self.trackedRidershipLogDict = dict()
        self.auxiliaryRidershipLogDict = dict()
        self.servedStationSet = dict()
        
        for trainName, train in transSys.trainDict.items():
            
            #generate train-specific dict
            self.totalRidershipLogDict[trainName] = dict()
            self.trackedRidershipLogDict[trainName] = dict()
            self.auxiliaryRidershipLogDict[trainName] = dict()
            self.servedStationSet[trainName] = set(train.stationNameDict.values())
            
            for vehID, veh in train.vehicleDict.items():
                #copy for each vehicle the ridership dict
                self.totalRidershipLogDict[trainName][vehID] = veh.totalRidershipAtArrival
                self.trackedRidershipLogDict[trainName][vehID] = veh.trackedRidershipAtArrival
                self.auxiliaryRidershipLogDict[trainName][vehID] = veh.auxiliaryRidershipAtArrival
