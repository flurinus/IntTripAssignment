from activity import Activity
from parameter import Parameter
from methodLibrary import weightedChoice

class Pedestrian:
    
    def __init__(self, origNode, destNode, depTime, trainList, transferStationName, pedNet, transSys, persMem, param):

        assert(origNode in pedNet.graph), "Pedestrian walking network does not contain node %s" % origNode
        assert(pedNet.graph.out_degree(origNode)==1), \
            "out_degree of origNode %s is %s instead of 1" % (origNode, pedNet.graph.out_degree(origNode))
        self.origNode = origNode
        origLink = pedNet.graph.out_edges(origNode)[0]
        self.origLinkID = pedNet.streamIDDictRev[origLink]
        origAreaName = pedNet.linkIDAreaIDDict[self.origLinkID]
        self.origStationName = pedNet.areaStationDict[origAreaName]
        
        assert(destNode in pedNet.graph), "Pedestrian walking network does not contain node %s" % destNode
        assert(pedNet.graph.in_degree(destNode)==1), \
            "in_degree of destNode %s is %s instead of 1" % (destNode, pedNet.graph.in_degree(destNode))
        self.destNode = destNode
        destLink = pedNet.graph.in_edges(destNode)[0]
        self.destLinkID = pedNet.streamIDDictRev[destLink]
        destAreaName = pedNet.linkIDAreaIDDict[self.destLinkID]
        self.destStationName = pedNet.areaStationDict[destAreaName]
        
        self.param = param
        
        #distinguish corridor from auxiliary passengers
        #both origin and destination are in corridor
        if (not self.origNode == 'Gup') and (not self.destNode == 'Gdown'):
            self.auxiliaryPassenger = False
        #transfer passenger with either origin or destination in corridor
        elif (transferStationName is not None) and ((not self.origNode == 'Gup') or (not self.destNode == 'Gdown')):
            self.auxiliaryPassenger = False
        else:
            self.auxiliaryPassenger = True
        
        self.activitySequence = dict()
        self.episodeIDList = list()
        
        self.depTime = depTime
        
        assert( isinstance(trainList, list) )
        self.trainList = trainList
        
        assert(len(self.trainList) <= 2) #at most one transfer currently supported
        
        self.personalMemory = persMem
        self.chosenPathID = None
        self.chosenBoardLinkID = None
        
        self.logBook = list()
            
        self.curLinkID = None
        self.ridingTrainName = None
        self.curVehID = None
        self.seated = False
                
        actType = 'init'
        param = {'linkID':self.origLinkID,'depTime':self.depTime}
        self.activitySequence[len(self.activitySequence)] = Activity(actType,param)
        
        #local pedestrians
        if not self.trainList:
            actType = 'choosePathAndWalk'
            param = {'linkIDSet':{self.destLinkID}}
            self.activitySequence[len(self.activitySequence)] = Activity(actType,param)
            
        else:
            #first and second train coincide if only one train taken
            firstTrainID = self.trainList[0]
            secondTrainID = self.trainList[-1]
            
            assert(firstTrainID in transSys.trainDict.keys()), \
                "train %s found in traveler database (ROCKT), but not in train database (TRENTO: %s)" %\
                (firstTrainID, set(transSys.trainDict.keys()) )
            
            assert(secondTrainID in transSys.trainDict.keys()), \
                "train %s found in traveler database (ROCKT), but not in train database (TRENTO: %s)" %\
                (secondTrainID, set(transSys.trainDict.keys()) )
            
            firstTrain = transSys.trainDict[firstTrainID]
            secondTrain = transSys.trainDict[secondTrainID]
            
            origPlatformName = firstTrain.getPlatform(self.origStationName,pedNet)
            destPlatformName = secondTrain.getPlatform(self.destStationName,pedNet)
            
            actType = 'choosePathAndWalk'
            param = {'linkIDSet':self.getBoardLinkSet(origPlatformName,firstTrainID,transSys.trainDict,pedNet)}
            self.addActivity(Activity(actType,param))
            
            actType = 'waitAndBoard'
            param = {'trainID':firstTrainID}
            self.addActivity(Activity(actType,param))
                        
            if len(self.trainList) == 2:
                #transfer station must be set
                assert( transferStationName is not None)
                
                #connecting train must depart after feeding train arrives
                if (firstTrain.getArrTimeforStation(transferStationName) >= secondTrain.getDepTimeforStation(transferStationName)):
                    
                    if Parameter.showWarnings:
                        print( "Infeasible transfer in %s: train %s arriving at %s, whereas train %s departs already at %s" %\
                               (transferStationName, firstTrainID, firstTrain.getArrTimeforStation(transferStationName), secondTrainID, secondTrain.getDepTimeforStation(transferStationName)) )
                
#                 
                platformFirstTrain = firstTrain.platformNameDict[firstTrain.stationNameDictRev[transferStationName]]
                platformSecondTrain = secondTrain.platformNameDict[secondTrain.stationNameDictRev[transferStationName]]
                
                actType = 'rideAndAlight'
                param = {'platformName':platformFirstTrain}
                self.addActivity(Activity(actType,param))
                
                actType = 'choosePathAndWalk'
                param = {'linkIDSet':self.getBoardLinkSet(platformSecondTrain,secondTrainID,transSys.trainDict,pedNet)}
                self.addActivity(Activity(actType,param))
                                
                actType = 'waitAndBoard'
                param = {'trainID':secondTrainID}
                self.addActivity(Activity(actType,param))
        
            actType = 'rideAndAlight'
            param = {'platformName':destPlatformName}
            self.addActivity(Activity(actType,param))
            
            actType = 'choosePathAndWalk'
            param = {'linkIDSet':{self.destLinkID}}
            self.addActivity(Activity(actType,param))
            
        actType = 'exit'
        param = dict()
        self.activitySequence[len(self.activitySequence)] = Activity(actType,param)
            
    def getRelevantTravelCost(self):
        
        if self.auxiliaryPassenger == True:
            return 0
        else:            
            return self.totalTravelUtility
        
    
    def logEntry(self, pedNet, transSys, env):
        
        logTime = env.now
        
        #pedestrian may not walk and ride at the same time
        assert( not ((self.curLinkID is not None) and (self.ridingTrainName is not None)) )
        
        if self.curLinkID is not None:
            curAreaID = pedNet.getAreaIDFromLinkID(self.curLinkID)
            curArea = pedNet.getArea(curAreaID)
            density = curArea.resource.count/curArea.resource.areaSize
            
            logEntry = "on link %s, density: %.3f ped/m2" % (str(pedNet.getLinkNodes(self.curLinkID)), density)
            
            #add entry in log book of stream
            curStream = pedNet.streamDict[self.curLinkID]
            curStream.arrivalLogBook.append(logTime)
            
        elif self.ridingTrainName is not None:
            trainVehicle = transSys.trainDict[self.ridingTrainName].vehicleDict[self.curVehID]
            
            percentLoading = trainVehicle.cabin.passengerLoad/trainVehicle.cabin.capacity*100
            
            logEntry = "on train %s in vehicleID %d, loading: %.2f%%" % (self.ridingTrainName, self.curVehID, percentLoading)
            
            if self.seated:
                logEntry += ", seated"
            else:
                logEntry += ", standing"
        else:
            logEntry = "exited"
            
        self.logBook.append([logTime,logEntry])
    
    def getLinkList(self, origLinkID, destLinkID, pedNet, popMemory):
        #discrete choice approach
        
        linkList = list()
        
        origNode = pedNet.getLinkDestNode(origLinkID)
        destNode = pedNet.getLinkOrigNode(destLinkID) 
        
        #if (origNode,destNode) not in popMemory.odPathDict:
            #shortestNodeList = pedNet.getShortestPath(origNode,destNode)
            #print("OD pair (%s,%s) is not connected. Shortest path: %s" % (origNode,destNode,shortestNodeList))
            
        pathSet = popMemory.odPathDict[origNode,destNode]
        
        #at least one path must exist
        assert(len(pathSet) > 0)
        
        if (len(pathSet) == 1):
            pathID = next(iter(pathSet))
            
        else:
            
            pathIDUtilDict = dict()
            
            for curPathID in pathSet:
                pathIDUtilDict[curPathID] = self.personalMemory.getExpPathUtility(curPathID)
                                
            pathID = weightedChoice(pathIDUtilDict,normalize=True)
            
            if self.chosenPathID is None:
                self.chosenPathID = pathID
            else:
                raise Exception("Error: Only a single choice per pedestrian allowed for learning. \
                    The pathSet %s contains more than one element." % str(pathSet))
                                                
        nodeList = popMemory.pathDict[pathID]
                
        #shortest route from downstream node of origLink to upstream node of destLink
        #nodeList = pedNet.getShortestPath(origNode,destNode)
        
        for linkNum in range(0,len(nodeList)-1):
            upNode = nodeList[linkNum]
            downNode = nodeList[linkNum+1]
            
            linkID = pedNet.getLinkID(upNode,downNode)
            
            linkList.append(linkID)
        
        #add destLinkID to linkList   
        linkList.append(destLinkID)
        
        return linkList

    def getBoardLinkSet(self, platformName, trainName, trainDict, pedNet):
                
        platform = pedNet.platformDict[platformName]

        boardLinkSet = platform.getBoardLinkIDSet(trainName, trainDict, pedNet)
        
        #at least one boarding link must exist
        assert(len(boardLinkSet) > 0)
        
        return boardLinkSet
    
    #obsolete
#     def chooseBoardLink(self, platformName, train, pedNet):
#         #choose boarding link based on historical utility
#         
#         print("THIS METHOD IS OBSOLETE AND SHOULD NEVER BE USED, NO?")
#         
#         boardLinkSet = self.getBoardLinkIDSet(self, platformName, train, pedNet)
#         
#         if (len(boardLinkSet) == 1):
#             boardLinkID = next(iter(boardLinkSet))
#             
#         else:
#    
#             boardLinkIDUtilDict = dict()
#             
#             for boardLinkID in boardLinkSet:
#                 boardLinkIDUtilDict[boardLinkID] = self.personalMemory.getExpBoardLinkUtility(boardLinkID)
# 
#             boardLinkID = weightedChoice(boardLinkIDUtilDict,normalize=True)
#             
#             if self.chosenBoardLinkID is None:
#                 self.chosenBoardLinkID = boardLinkID
#             else:
#                 raise Exception("Error: Only a single choice per pedestrian allowed for learning. \
#                      The boardLinkSet %s contains more than one element." % str(boardLinkSet))
#        
#         return boardLinkID 
    
        #obsolete
#     def getAlightingLinkID(self, platformName, transSys, pedNet):
#         #choose alighting link based on current train vehicle and link assignment fractions
#         
#         numVehicles = transSys.trainDict[self.ridingTrainName].numVehicles
#         
#         platform = pedNet.platformDict[platformName]
#         
#         alightLinkDict = platform.vehLinkAssg[numVehicles,self.curVehID]
#         
#         return weightedChoice(alightLinkDict) 
        
    #def getRoute(self, origNode, destNode, pedNet):
        #return pedNet.getShortestPath(self.origNode, self.destNode)
    
    def getCurStream(self, pedNet):
        return pedNet.getStream(self.curLinkID)
    
    def getArea(self, pedNet):
        self.getCurStream(pedNet).getArea()
        
    def getCurPlatform(self, pedNet):
        pass
                
    def getStreamTravelTime(self, pedNet):
        #get current stream
        curStream = pedNet.streamDict[self.curLinkID]
        
        #return travel time
        travelTime = curStream.getTravelTime(self.personalMemory.speedMultiplier)
                
        return travelTime
    
    def getNextLinkID(self, pedNet):
        # get current destination node
        curDestNode = pedNet.getLinkDestNode(self.curLinkID)
        
        # get shortest path from curDestNode to final destination
        remainingShortestPath = pedNet.getShortestPath(curDestNode,self.destNode)
        
        assert( (remainingShortestPath[0] == curDestNode) )
        
        nextLinkOrigNode = curDestNode
        nextLinkDestNode = remainingShortestPath[1]
                
        #get linkID of next link
        return pedNet.getLinkID(nextLinkOrigNode,nextLinkDestNode)
    
    def addActivity(self, activity):
            self.activitySequence[len(self.activitySequence)] = activity
     
    def propagate(self, simEnv, pedNet, transSys, popMemory):
        
        curActNumber = 0
        
        curEpisodeID = None
        #curEpisodeStartTime = 0
        curEpisodeUtility = 0
            
        self.totalTravelUtility = 0
        self.totalWalkUtility = 0
        self.totalWaitUtility = 0
        self.totalRideUtility = 0
        self.totalPenalty = 0 #for missed trains, or chance to miss train
        
        while(curActNumber < len(self.activitySequence) ):
            curActivity = self.activitySequence[curActNumber]
            
            actType = curActivity.actType
            param = curActivity.param
            
            #episodes: choosePathAndWalk + waitAndBoard, choosePathAndWalk + Exit, rideAndAlight 
            
            if ('init' == actType):
                
                #delay pedestrian by his departure time
                yield simEnv.timeout(param['depTime'])
                timeDep = simEnv.now
                
                #initialize pedestrian on desired link
                linkID = param['linkID']
                
                #get area of origin link
                origArea = pedNet.getAreaFromLinkID(linkID)
                self.resReqEvent = origArea.getResReqEvent()
                
                #try to get slot on area and update current link 
                yield self.resReqEvent
                self.curLinkID = linkID
                
                #no delay between planned and actual initialization time
                timeAdmitted = simEnv.now
                
                if (timeAdmitted > timeDep):
                    delayStr = "Late initialization by %.1f on link (%s,%s), admitted at %.1f instead of %.1f"\
                    % (timeAdmitted-timeDep, pedNet.streamIDDict[self.curLinkID], timeAdmitted, timeDep)
                    
                    print(delayStr)
                            
            elif ('choosePathAndWalk' == actType):
                
                assert('linkIDSet' in param)
                destLinkIDSet = param['linkIDSet']
                
                #set of all feasible paths to any of the destLinkIDs
                pathIDset = set()
                
                origNode = pedNet.getLinkOrigNode(self.curLinkID)
                         
                for destLinkID in destLinkIDSet:
                    destNode = pedNet.getLinkDestNode(destLinkID)                    
                    curPathIDSet = popMemory.getPathSet(origNode,destNode,pedNet)
                    
                    pathIDset.update(curPathIDSet)
                    
                #at least one path must exist
                assert(len(pathIDset) > 0)
                
                #dictionary of logsum of utility of all decision paths that are compatible with a given path ID
                pathIDUtilDict = dict()
                
                #previous episode: update choice set for correct computation of logsum
                if len(self.episodeIDList) > 0:
                    updateChoiceTree = True
                    prevEpisode = self.personalMemory.episodeDict[self.episodeIDList[-1]]
                else:
                    updateChoiceTree = False
                        
                #simple path choice model that neglects correlation/overlap
                #reasonable approximation for paid areas with unique path between any OD (no path choice would be even needed)
                for pathID in pathIDset:
                    pathIDUtilDict[pathID] = self.personalMemory.getPathPotential(curActNumber,pathID)
                    
                    if updateChoiceTree:
                        #probability of availability of a path is always one
                        prevEpisode.nextEpisodeDict[(curActNumber,pathID)] = 1
                                    
                chosenPathID = weightedChoice(pathIDUtilDict, normalize=True)
                 
                curEpisodeID = (curActNumber,chosenPathID)
                self.episodeIDList.append(curEpisodeID)
                self.personalMemory.initializeEpisode(curEpisodeID)
                #curEpisodeStartTime = simEnv.now
                curEpisodeUtility = 0
                
                timeLinkAdmission = simEnv.now #register time at which pedestrian has been admitted to current link              
                
                linkList = popMemory.getLinkList(chosenPathID,pedNet)
                
                if not linkList:
                    #if linkList is empty, transfer on same boarding area
                    #change pedestrian from alighting to boarding link
                    alightLinkName = pedNet.streamIDDict[self.curLinkID]
                    boardLinkName = alightLinkName[::-1]
                    boardLinkID = pedNet.streamIDDictRev[boardLinkName]
                    
                    linkList = [boardLinkID]
                    
                assert(linkList), "linkList must not be empty"
                
                for nextLinkID in linkList:
                    curAreaID = pedNet.getAreaIDFromLinkID(self.curLinkID)
                    curArea = pedNet.getArea(curAreaID)
                    curArea.resource.updateCost() #required for pedestrians alighting from train
                    
                    nextAreaID = pedNet.getAreaIDFromLinkID(nextLinkID)
                                        
                    #if changing area, need to book slot in new area and release old
                    if (curAreaID != nextAreaID):
                        nextArea = pedNet.getArea(nextAreaID)
                        
                        #get interface
                        interfaceID = pedNet.getInterfaceID(curAreaID,nextAreaID)
                        
                        if interfaceID is not None:
                            interface = pedNet.getInterface(interfaceID)
                            
                            #get wait time needed to enforce flow capacity at interface
                            interfaceWaitTime = interface.getWaitTime(simEnv)
                            
                            #wait at interface, while remaining registered on current area
                            yield simEnv.timeout(interfaceWaitTime)
                            
                        elif Parameter.showWarnings:
                            pedNet.interfaceDebugSet.add("No interface between areas %s and %s available." % (curAreaID,nextAreaID))
                        
                        
                        #once interface passed, prepare accessing of area
                        nextAreaResReqEvent = nextArea.getResReqEvent()
                        
                        #try to get slot on area, release previous area, and update area request handler
                        yield nextAreaResReqEvent
                        curArea.getRelease(self.resReqEvent)
                        self.resReqEvent = nextAreaResReqEvent
                    
                    #add walking cost to travel cost of episode
                    if simEnv.now != timeLinkAdmission:
                        curArea.resource.updateCost()
                        walkingCost = curArea.getWalkingCost(timeLinkAdmission,simEnv.now)
                        curEpisodeUtility -= walkingCost

                        #register time of admittance to new link
                        timeLinkAdmission = simEnv.now
                    
                    #update link 
                    self.curLinkID = nextLinkID
                    
                    if Parameter.textOutput or self.param.isFinalInstance:
                        self.logEntry(pedNet,transSys,simEnv)
                    
                    #book pedestrian during walking
                    yield simEnv.timeout(self.getStreamTravelTime(pedNet))
                
                #generate time stamp in cumulative area travel cost and add cost for last link traversal
                curArea = pedNet.getArea( pedNet.getAreaIDFromLinkID(self.curLinkID) )
                curArea.resource.updateCost()
                walkingCost = curArea.getWalkingCost(timeLinkAdmission,simEnv.now)
                curEpisodeUtility -= walkingCost
                
                self.totalWalkUtility += curEpisodeUtility

                                
            elif ('waitAndBoard' == actType):
                
                trainName = param['trainID']
                train = transSys.trainDict[trainName]
                
                assert(self.curLinkID in pedNet.boardingLinkPlatformDict.keys()), \
                    "link %s %s not a boarding link, pedestrian awaiting train %s may have got lost at time %.2f. \nLogBook of affected traveler:\n%s\nActivity Sequence:\n%s" % \
                    (self.curLinkID, pedNet.streamIDDict[self.curLinkID], trainName, simEnv.now, ''.join('{}: {}\n'.format(*logEntry) for logEntry in self.logBook), "".join("{}: {}\n".format(k, v) for k, v in self.activitySequence.items()) )
                
                curPlatformName = pedNet.boardingLinkPlatformDict[self.curLinkID]
                
                curAreaID = pedNet.getAreaIDFromLinkID(self.curLinkID)
                curArea = pedNet.getArea(curAreaID)
                
                timePlatformArrival = simEnv.now
                                                
                #if train already departed
                if ( train.getDepartureEvent(curPlatformName).processed ):
                    #print('Missed my train. Will leave the simulation.')
                    
                    #penalize missing the train with a high travel cost
                    curEpisodeUtility -= Parameter.costMissedTrain
                    self.totalPenalty -= Parameter.costMissedTrain
                
                    #increase walking speed multiplier
                    self.personalMemory.speedMultiplier = min(self.personalMemory.speedMultiplier*Parameter.speedMultiplierIncrease,Parameter.maxSpeedMultiplier)
                    
                    #add entry in log book
                    self.logBook.append([simEnv.now,"Missed train. Leaving simulation."])
                    
                    if Parameter.showWarnings and self.personalMemory.speedMultiplier == Parameter.maxSpeedMultiplier:
                        print("Missed train %s: Reached platform %s %.1fs late, train left at %.1f. (Using maximum speed multiplier %.1f)." % (trainName, curPlatformName, timePlatformArrival-train.getDepTimeForPlatform(curPlatformName), train.getDepTimeForPlatform(curPlatformName), self.personalMemory.speedMultiplier) )
                    
                    #leave simulation
                    curArea.getRelease(self.resReqEvent)
                    simEnv.exit()
                    
                else:
                    yield train.getArrivalEvent(curPlatformName)
                    
                    platform = pedNet.platformDict[curPlatformName]
                    
                    #add available set of vehicles to choice set of current episode
                    curEpisode = self.personalMemory.episodeDict[self.episodeIDList[-1]]
                    
                    
                    vehIDAssgFrac = platform.getBoardAssgFrac(self.curLinkID, trainName,\
                        transSys.trainDict, pedNet.streamIDDictRev)
                    
                    #Availability of car given by assignment probability (no active choice!)                    
                    for vehID, vehChoiceProb in vehIDAssgFrac.items():
                        curEpisode.nextEpisodeDict[(curActNumber+1,vehID)] = vehChoiceProb
                        
                    #on lateral platform sectors, train cars may not cover full sector length
                    #given a uniform distribution along a sector represented by a boarding link, service probability given by 
                    trainServiceProbability = platform.boardLinkServiceProbability[trainName][self.curLinkID]
                    
                    #penalty due to limited service (requiring walking) approximated by transfer penalty
                    penaltyNoLocalTrainService = (1-trainServiceProbability)*Parameter.penaltyTrans
                    
                    #penalize additional walking
                    curEpisodeUtility -= penaltyNoLocalTrainService
                    self.totalPenalty -= penaltyNoLocalTrainService
                    
                    #get train vehicle from boarding link (weighted random choice)
                    trainVehID = platform.assignVehicle(self.curLinkID, trainName, transSys.trainDict, pedNet.streamIDDictRev) 
                    #weightedChoice(platform.linkVehAssg[train.numVehicles,self.curLinkID])
                    trainVehicle = train.vehicleDict[trainVehID]
                    
                    #once train has arrived, queue up to board
                    with trainVehicle.requestBoarding() as boardReq: #generate request event
                        #wait for access
                        yield boardReq
                        
                        #check out from area
                        curArea.getRelease(self.resReqEvent)
                        self.curLinkID = None
                        self.ridingTrainName = param['trainID']
                        self.curVehID = trainVehID
                        
                        #waiting cost
                        #account for waiting cost except if pedestrian arrived before simulation started
                        if not timePlatformArrival < self.param.dateStartSec:
                            waitingCost = curArea.getWaitingCost(timePlatformArrival,simEnv.now)
                            curEpisodeUtility -= waitingCost
                            self.totalWaitUtility -= waitingCost
                        
                        #transfer cost: can be applied upfront as number of transfers is known in advance
                        #curEpisodeUtility -= Parameter.penaltyTrans
                        
                        #block door while boarding
                        boardingTime = trainVehicle.boardServTime()
                        yield simEnv.timeout(boardingTime)
                        
                        #consider boarding time in travel cost (probably negligible)
                        boardWaitCost = boardingTime*Parameter.betaIVTZero #assume boarding time waited as IVT
                        curEpisodeUtility -= boardWaitCost
                        self.totalWaitUtility -= boardWaitCost
                 
                        #increment passenger count
                        trainVehicle.cabin.passengerLoad += 1
                        if self.auxiliaryPassenger:
                            trainVehicle.cabin.loadAuxiliaryPassengers += 1
                        else:
                            trainVehicle.cabin.loadTrackedPassengers += 1

                    if Parameter.textOutput or self.param.isFinalInstance:
                        self.logEntry(pedNet,transSys,simEnv)
                 
                self.personalMemory.memorizeEpisode(curEpisodeID,curEpisodeUtility)
                self.totalTravelUtility += curEpisodeUtility
            
            elif ('rideAndAlight' == actType):
                
                assert(self.ridingTrainName is not None and self.curVehID is not None)
                
                train = transSys.trainDict[self.ridingTrainName]
                trainVehicle = train.vehicleDict[self.curVehID]
                
                curEpisodeID = (curActNumber,self.curVehID)
                self.personalMemory.initializeEpisode(curEpisodeID)
                self.episodeIDList.append(curEpisodeID)
                #curEpisodeStartTime = simEnv.now
                curEpisodeUtility = 0
                timeRideStart = simEnv.now
                
                #cabin request and train arrival event
                self.seatReqEvent = trainVehicle.cabin.request()
                arrEvent = train.getArrivalEvent(param['platformName'])
                assert(arrEvent.processed is False), \
                    "Train %s should not have arrived yet on %s at %.2f. Passenger details: %s." %\
                    (self.ridingTrainName, param['platformName'], simEnv.now, self.activitySequence)
                
                #wait for free cabin or train arrival
                nextEvent = yield self.seatReqEvent | arrEvent
                
                #if no space available until arrival
                if arrEvent in nextEvent:
                    timeTrainArrival = simEnv.now
                    
                    #manually compute standing cost
                    trainVehicle.cabin.updateCost()
                    
                    ridingCost = trainVehicle.getRidingCostStanding(timeRideStart,timeTrainArrival)
                    curEpisodeUtility -= ridingCost
                
                #if a seating space is available
                else:
                    timeSeated = simEnv.now
                    self.seated = True
                    
                    ridingCost = trainVehicle.getRidingCostStanding(timeRideStart,timeSeated)
                    curEpisodeUtility -= ridingCost
                
                    if Parameter.textOutput or self.param.isFinalInstance:
                        self.logEntry(pedNet,transSys,simEnv)
                    
                    #wait for vehicle to arrive
                    yield arrEvent
                    timeTrainArrival = simEnv.now
                    
                    #charge travel cost during seated part
                    trainVehicle.cabin.updateCost()
                    ridingCost = trainVehicle.getRidingCostSeated(timeSeated,timeTrainArrival)
                    curEpisodeUtility -= ridingCost

                #once arrived, leave cabin or revoke cabin request event
                trainVehicle.cabin.release(self.seatReqEvent)
                self.seated = False
                if Parameter.textOutput or self.param.isFinalInstance:
                    self.logEntry(pedNet,transSys,simEnv)
                
                #get alighting link
                #alightLinkID = self.getAlightingLinkID(param['platformName'],transSys,pedNet) #obsolete
                alightingPlatformName = param['platformName']
                alightingPlatform = pedNet.platformDict[alightingPlatformName]
                alightLinkID = alightingPlatform.assignAlightLink(self.ridingTrainName, \
                    transSys.trainDict, self.curVehID, pedNet.streamIDDictRev)
                
                alightAreaID = pedNet.getAreaIDFromLinkID(alightLinkID)
                alightArea = pedNet.getArea(alightAreaID)
                alightAreaResReqEvent = alightArea.getResReqEvent()
                
                #once train has arrived, queue up to alight
                with trainVehicle.requestAlighting() as alightReq: #generate request event
                    yield alightReq #wait for access
                    alightingTime = trainVehicle.alightServTime()
                    yield simEnv.timeout(alightingTime) #block door while boarding
                    
                    #once able to use door, request space on area
                    yield alightAreaResReqEvent
                    self.ridingTrainName = None
                    self.curVehID = None
                    self.resReqEvent = alightAreaResReqEvent
                    
                    #decrement passenger count
                    assert(trainVehicle.cabin.passengerLoad > 0)
                    trainVehicle.cabin.passengerLoad -= 1
                    if self.auxiliaryPassenger:
                        trainVehicle.cabin.loadAuxiliaryPassengers -= 1
                    else:
                        trainVehicle.cabin.loadTrackedPassengers -= 1
                    
                    #update link 
                    self.curLinkID = alightLinkID
                                
                #charge travel cost during alighting, requiring updating of cost
                trainVehicle.cabin.updateCost() 
                timeOnPlatform = simEnv.now
                ridingCost = trainVehicle.getRidingCostStanding(timeTrainArrival,timeOnPlatform)
                curEpisodeUtility -= ridingCost
                
                self.personalMemory.memorizeEpisode(curEpisodeID,curEpisodeUtility)
                self.totalTravelUtility += curEpisodeUtility
                self.totalRideUtility += curEpisodeUtility
                
            elif ('exit' == actType):
                #release current area
                curAreaID = pedNet.getAreaIDFromLinkID(self.curLinkID)
                curArea = pedNet.getArea(curAreaID)
                curArea.getRelease(self.resReqEvent)
                
                #set current link to None
                self.curLinkID = None
                
                #memorize episode and update travel cost                
                self.personalMemory.memorizeEpisode(curEpisodeID,curEpisodeUtility)
                self.totalTravelUtility += curEpisodeUtility
                           
                #display pedestrian state (debugging)
                if Parameter.textOutput or self.param.isFinalInstance:
                    self.logEntry(pedNet,transSys,simEnv)
                

            else:
                raise KeyError('unknown actType ' + actType)
             
            curActNumber += 1
        
        simEnv.exit()