import numpy as np
from methodLibrary import weightedChoice


class TrainPlatform(object):

    def __init__(self, trainInterfaceNodes, areaLimitCoord, stopSignalPos, usageDirection, \
                 streamIDDict, streamIDDictRev, linkIDAreaIDDict, areaStationDict, netGraph):
        
        #generate board and alight link id sets
        self.boardLinkIDSet = set()
        self.alightLinkIDSet = set()
        
        for interfaceNode in trainInterfaceNodes:
            
            #interfaceNode should be a lateral node
            assert( netGraph.in_degree( interfaceNode ) == 1)
            assert( netGraph.out_degree( interfaceNode ) == 1)
            
            #interfaceNode of the form AN151T, and adjacent AN151 (without trailing T)
            adjacentNode = interfaceNode[:-1]
            
            boardLink = (adjacentNode, interfaceNode)
            alightLink = (interfaceNode, adjacentNode)
            
            #boarding and alighting links need to exist
            assert( boardLink in streamIDDictRev.keys() ), "boardLink %s does not exist" % boardLink
            assert( alightLink in streamIDDictRev.keys() ), "alightLink %s does not exist" % alightLink
            
            boardLinkID = streamIDDictRev[boardLink]
            alightLinkID = streamIDDictRev[alightLink]
            
            self.boardLinkIDSet.add( boardLinkID )
            self.alightLinkIDSet.add( alightLinkID )
        
        #infer station from random platform area, use 
        randomLinkID = next(iter( self.boardLinkIDSet ) )
        randomPlatformAreaName = linkIDAreaIDDict[ randomLinkID ]
        self.stationName = areaStationDict[randomPlatformAreaName]
        
        #generate local dict of interface area delimiter coordinates
        self.areaDelimiterCoord = dict()        
        for interfaceNode in trainInterfaceNodes:
            self.areaDelimiterCoord[interfaceNode] = areaLimitCoord[interfaceNode]
        
        #store stop signal position dict and usage direction of platform
        self.stopSignalPos = stopSignalPos
        
        assert( usageDirection == "right" or usageDirection == "left")
        self.usageDirection = usageDirection
        
        #dictionaries containing assignment fractions for all trains served by platform
        self.trainVehicleToAlightLinkFrac = dict()
        self.boardLinkToTrainVehicleFrac = dict()
        self.boardLinkServiceProbability = dict()
    
    #randomly assigns vehicle to passenger on boardLink
    def assignVehicle(self, boardLinkID, trainName, trainDict, streamIDDictRev):
        #dictionary containing for each vehID an assignment probability
        vehIDAssgFrac = self.getBoardAssgFrac(boardLinkID, trainName, trainDict, streamIDDictRev)
        
        return weightedChoice(vehIDAssgFrac)
    
    #randomly assigns alightLink to passenger in vehicle #vehID    
    def assignAlightLink(self, trainName, trainDict, vehID, streamIDDictRev):
        #dictionary of alighting links and corresponding assignment probabilities
        alightLinkAssgFrac = self.getAlightAssgFrac(trainName, trainDict, vehID, streamIDDictRev)
        
        return weightedChoice(alightLinkAssgFrac)
    
    #get set of boarding links for a given train (required for choice of boarding link)
    def getBoardLinkIDSet(self, trainName, trainDict, pedNet):
        
        if not (trainName in self.boardLinkToTrainVehicleFrac):
            self.computePlatformTrainAssignmentMap(trainName, trainDict, pedNet.streamIDDictRev)
            
        boardLinkIDSet = set()
        
        for (boardLinkID, _) in self.boardLinkToTrainVehicleFrac[trainName].keys():
            
            assert(boardLinkID in pedNet.streamIDDict.keys() )
            #boardLinkID = pedNet.streamIDDictRev[boardLink]
            boardLinkIDSet.add(boardLinkID)
            
        return boardLinkIDSet
        
       
    def getBoardAssgFrac(self, boardLinkID, trainName, trainDict, streamIDDictRev):
        
        if not (trainName in self.boardLinkToTrainVehicleFrac):
            self.computePlatformTrainAssignmentMap(trainName, trainDict, streamIDDictRev)
        
        vehIDAssgFrac = dict()
        
        for (curBoardLinkID, curVehID), assgFrac in self.boardLinkToTrainVehicleFrac[trainName].items():
            if curBoardLinkID == boardLinkID:
                assert( curVehID not in vehIDAssgFrac.keys() ) #should never occur
                vehIDAssgFrac[curVehID] = assgFrac
                
        return vehIDAssgFrac
                
    
    def getAlightAssgFrac(self, trainName, trainDict, vehID, streamIDDictRev):
        
        if not (trainName in self.trainVehicleToAlightLinkFrac):
            self.computePlatformTrainAssignmentMap(trainName, trainDict, streamIDDictRev)
            
        alightLinkAssgFrac = dict()
        
        for (curVehID, curAlightLinkID), assgFrac in self.trainVehicleToAlightLinkFrac[trainName].items():
            if vehID == curVehID:
                assert( curAlightLinkID not in alightLinkAssgFrac.keys() )
                alightLinkAssgFrac[curAlightLinkID] = assgFrac 
        
        return alightLinkAssgFrac
    
    def getStopPosition(self, trainName, trainDict):
        train = trainDict[trainName]
        numVehicles = train.numVehicles
        
        if train.numVehicles in self.stopSignalPos.keys():
            trainHeadPos = self.stopSignalPos[ numVehicles ]
        else:
            trainLengthList = sorted( self.stopSignalPos.keys() )
            stopPosList = [ self.stopSignalPos[numCars] for numCars in trainLengthList]
            trainHeadPos = np.interp(numVehicles, trainLengthList, stopPosList)
                        
        return trainHeadPos
        
        
    def computePlatformTrainAssignmentMap(self, trainName, trainDict, streamIDDictRev):
        
        train = trainDict[trainName]
        
        trainHeadPos = self.getStopPosition(trainName, trainDict)
        
        carLength = train.length / train.numVehicles
        
        trainCarCoordinates = dict()
        
        #compute left and right (lower and upper) position of each train car
        for carID in range(0, train.numVehicles):
            
            if self.usageDirection == "right":
                carLeftEnd = trainHeadPos - (carID + 1) * carLength
                carRightEnd = trainHeadPos - carID * carLength
            
            elif self.usageDirection == "left":
                carLeftEnd = trainHeadPos + carID * carLength
                carRightEnd = trainHeadPos + (carID + 1) * carLength
            
            trainCarCoordinates[carID] = [carLeftEnd,carRightEnd]
                    
 
        platformAreaToTrainCarAssignment = dict()
        trainCarToPlatformAreaAssignment = dict()

        #compute assignment fractions
        for carID, carCoords in trainCarCoordinates.items():
            carLo = carCoords[0]
            carUp = carCoords[1]
            
            assert(carUp > carLo)
            
            for interfaceNode, delimiterCoords in self.areaDelimiterCoord.items():
                platLo = delimiterCoords[0]
                platUp = delimiterCoords[1]
                
                assert(platUp > platLo)
                
                platAreaLength = platUp - platLo
                
                #train car and platform area overlap
                if ( ( carLo < platUp ) and ( platLo < carUp ) ):
                    
                    overlap = min(carUp, platUp) - max(carLo, platLo)
                    
                    #train car-to-platform area assignment rate
                    carToAreaFraction = overlap/carLength
                    
                    #platform area-to-train car assignment rate
                    areaToCarFraction = overlap/platAreaLength
                    
                    #store
                    trainCarToPlatformAreaAssignment[carID,interfaceNode] = carToAreaFraction
                    platformAreaToTrainCarAssignment[interfaceNode,carID] = areaToCarFraction
        
        #consistency check: train car-to-platform area assignment fraction need to sum to 1 by definition (otherwise platform is too short)
        for carID in range(0, train.numVehicles):
            cumFrac = 0
            
            for (curCarID, _), frac in trainCarToPlatformAreaAssignment.items():
                
                if curCarID == carID:
                    cumFrac += frac
            
            #cumulative fraction must be smaller than one, allowing for numerical error
            assert(cumFrac <= 1.001)
            
            #alighting passengers must be assigned a platform node with certainty
            if cumFrac < 0.999:
                print("Train car %i/%d not fully served (cumFrac = %f)" % (carID, train.numVehicles, cumFrac) )
                
                print("train name: %s" % trainName)
                print("train head pos: %s" % trainHeadPos)
                print("trainCarCoordinates: %s" % trainCarCoordinates)
                print("self.areaDelimiterCoord: %s" % self.areaDelimiterCoord)
                print("trainCarToPlatformAreaAssignment: %s" % trainCarToPlatformAreaAssignment)
                
                
                assert(cumFrac > 0.999)
        
        
        #platform area-to-train car assignment fractions need to be scaled such that they sum up to one, unless there is no train car serving an area at all
        
        #compute cumulative platform area fractions
        cumBoardNodeFrac = dict()
        for platNode, carID in set(platformAreaToTrainCarAssignment.keys()):
            if platNode not in cumBoardNodeFrac.keys():
                cumBoardNodeFrac[platNode] = 0
            
            cumBoardNodeFrac[platNode] += platformAreaToTrainCarAssignment[platNode, carID]
        
        #normalize assignment fractions to sum up to 1
        for platNode, cumFrac in cumBoardNodeFrac.items():
            #allow for numerical error
            assert(cumFrac <= 1.001 and cumFrac > 0)
            
            #rescale fractions if needed
            if cumFrac < 1:
                    
                for (curBoardNode, curCarID) in platformAreaToTrainCarAssignment.keys():
                    
                    #iterate through affected fractions
                    if curBoardNode == platNode:
                        
                        platformAreaToTrainCarAssignment[curBoardNode,curCarID] /= cumFrac         
                    
        #generate required assignment fraction dictionaries in required format        
        trainCarToAlightLinkFrac = dict()
        boardLinktoTrainCarFrac = dict()
        
        for (carID, platNode), frac in trainCarToPlatformAreaAssignment.items():
            
            #nodes are called N*T and N*, e.g. AN51T and AN51
            alightLink = (platNode, platNode[:-1])
            alightLinkID = streamIDDictRev[alightLink]
            
            trainCarToAlightLinkFrac[carID, alightLinkID] = frac
            
        for (platNode, carID), frac in platformAreaToTrainCarAssignment.items():
            
            #nodes are called N*T and N*, e.g. AN51T and AN51
            boardLink = (platNode[:-1], platNode)
            boardLinkID = streamIDDictRev[boardLink]
            
            boardLinktoTrainCarFrac[boardLinkID, carID] = frac
            
        boardLinkServicePobability = dict()
        
        for platNode, frac in cumBoardNodeFrac.items():
            #nodes are called N*T and N*, e.g. AN51T and AN51
            boardLink = (platNode[:-1], platNode)
            boardLinkID = streamIDDictRev[boardLink]
            
            boardLinkServicePobability[boardLinkID] = frac
            
        #store assignment fraction for current train in platform dictionary
        self.trainVehicleToAlightLinkFrac[trainName] = trainCarToAlightLinkFrac
        self.boardLinkToTrainVehicleFrac[trainName] = boardLinktoTrainCarFrac
        self.boardLinkServiceProbability[trainName] = boardLinkServicePobability
    