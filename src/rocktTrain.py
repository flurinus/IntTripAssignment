from parameter import Parameter
from scipy.optimize import nnls
import numpy as np
from random import random
from rocktGateLine import RocktGateLine

class RocktTrain(object):

    def __init__(self):
        
        self.trackNumber = dict()
        
        self.ridershipTowards = dict()
        
        self.boardOutgoing = dict()
        self.alightIncoming = dict()
        self.boardTransfer = dict()
        self.alightTransfer = dict()
        
        self.totBoardSynthesized = dict()
        self.totAlightSynthesized = dict()
        
        self.corridorFlag = False
        
        self.passODEst = dict()
        self.odRatio = dict()
        
        self.destListDict = dict()
        self.destCumProbDict = dict()
        
        self.origListDict = dict()
        self.origCumProbDict = dict()
    
        self.entranceGateLineDict = dict()
        self.exitGateLineDict = dict()
        
    def addSynthesizedPassenger(self, origStation, destStation):
        
        if not origStation in self.totBoardSynthesized.keys():
            self.totBoardSynthesized[origStation] = 0
        
        self.totBoardSynthesized[origStation] += 1
        
        if not destStation in self.totAlightSynthesized.keys():
            self.totAlightSynthesized[destStation] = 0
        
        self.totAlightSynthesized[destStation] += 1
    
    #returns True if passenger sampled to take a transfer train at destination
    #required for population synthesis to avoid double generation of travelers    
    def transferAtDestination(self, stationName):
        #if no transfers recorded for given stationName and train, probability of transferring is zero
        if not stationName in self.alightTransfer.keys():
            transfer = False
        
        else:
            numTransfer = self.alightTransfer[stationName]
            
            numFinalDest = self.alightIncoming[stationName]
            
            totNumAlight = numTransfer+numFinalDest
            ratioTransfer = numTransfer/totNumAlight
            
            randomDraw = random()
            
            if randomDraw <= ratioTransfer:
                transfer = True
            else:
                transfer = False
            
        return transfer
    
    def chooseEntranceTime(self, stationName, entranceGate):
        
        if stationName == "upstream":
            entranceTime = 0
        
        else:
            #if data is complete, other passengers of train have entered
            assert( stationName in self.entranceGateLineDict.keys() )
            
            curGateLine = self.entranceGateLineDict[stationName] 
            
            entranceTime = curGateLine.drawEntranceTime(entranceGate)
        
        return entranceTime
    
        
    def sampleDestinationStationAndExitGate(self, curStation):
        
        #if train serves corridor
        if (self.corridorFlag == True):
            destStation = self.sampleDestination(curStation)
            assert(destStation in Parameter.stationSet), \
                "All passengers of corridor trains need to terminate at a modeled station (current destination: %s)." % destStation
            
            #given destination station, draw check out node
            destNode = self.chooseExitGate(destStation)
            
        #train not serving corridor
        else:
            destStation = "downstream"
            destNode = Parameter.downstreamNode
    
        return destNode, destStation
    
    def sampleOriginStationAndEntranceGate(self, curStation):
    
        #draw origin station and origin node
        if (self.corridorFlag == True):
            #draw origin station
            origStation = self.sampleOrigin(curStation)
                                
            #given origin station, draw entrance node
            origNode = None
                    
            if origStation in Parameter.stationSet:
                #need to draw entrance node
                origNode = self.chooseEntranceGate(origStation)
                        
                #need to draw entrance time, depending on entranceNodeID (unique)
                origTime = self.chooseEntranceTime(origStation, origNode)
                    
            else:
                assert(origStation == "upstream")
                origNode = Parameter.upstreamNode
                origTime = 0
                
        #train not serving corridor
        else:
            origStation = "upstream"
            origNode = Parameter.upstreamNode    
            origTime = 0
                
        return origTime, origNode, origStation
    
    
    def printGateUsage(self):
        
        printString = "entrance gate usage:\n"
        
        for stationName,gateLine in self.entranceGateLineDict.items(): 
            printString += "%s: %s\n" % (stationName, gateLine)
        
        printString += "\nexit gate usage:\n"    
        
        for stationName,gateLine in self.exitGateLineDict.items(): 
            printString += "%s: %s\n" % (stationName, gateLine)
            
        return printString
    
    def chooseEntranceGate(self, stationName):
        
        if stationName == "upstream":
            return Parameter.upstreamNode
         
        elif stationName == "downstream":
            print("Warning: Entrance gate cannot be downstream.")
            return Parameter.downstreamNode
        
        else:
            #if data is complete, other passengers of train have entered
            assert( stationName in self.entranceGateLineDict.keys() )
            
            curGateLine = self.entranceGateLineDict[stationName] 
            
            return curGateLine.drawEntranceGate()
    
    def chooseExitGate(self, stationName):
        
        if stationName == "upstream":
            print("Warning: Exit gate cannot be upstream.")
            return Parameter.upstreamNode
         
        elif stationName == "downstream":
            return Parameter.downstreamNode
        
        else:
            #if data is complete, other passengers of train have exited
            assert( stationName in self.exitGateLineDict.keys() )
            
            curGateLine = self.exitGateLineDict[stationName] 
            
            return curGateLine.drawExitGate()
    
    def addEntranceGateUsage(self, stationName, gateNode, entranceTime, numTravelers):
        
        assert(stationName in Parameter.stationSet)
        
        if stationName in self.entranceGateLineDict:
            curGateLine = self.entranceGateLineDict[stationName]
        else:
            curGateLine = RocktGateLine()
            self.entranceGateLineDict[stationName] = curGateLine 
            
        curGateLine.addEntranceUsage(gateNode, entranceTime, numTravelers)
    
    def addExitGateUsage(self, stationName, gateNode, exitTime, numTravelers):
        
        assert(stationName in Parameter.stationSet)
        
        if stationName in self.exitGateLineDict:
            curGateLine = self.exitGateLineDict[stationName]
        else:
            curGateLine = RocktGateLine()
            self.exitGateLineDict[stationName] = curGateLine 
            
        curGateLine.addExitUsage(gateNode, exitTime, numTravelers)

    def sampleOrigin(self, curStationName):
        
        if curStationName in self.origListDict.keys():
            origList = self.origListDict[curStationName]
            origCumProbList = self.origCumProbDict[curStationName]
        
        else:
            #generate set of all OD pairs
            odPairSet = set(self.odRatio.keys())
            
            origList = list()
            cumDestFlowList = list()
            origCumProbList = list()
            
            totDestFlow = 0
            
            for odPair in odPairSet:
                if odPair[1] == curStationName:
                    
                    origStation = odPair[0]

                    origFlow = self.numBoardings(origStation)
                    odProb = self.odRatio[odPair]
                    
                    odFlow = origFlow*odProb
                    
                    totDestFlow += odFlow
                    
                    origList.append( origStation )
                    cumDestFlowList.append( totDestFlow )

            #compute origin split fractions
            for odFlow in cumDestFlowList:
                origCumProbList.append( odFlow/totDestFlow )
                
            self.origListDict[curStationName] = origList
            self.origCumProbDict[curStationName] = origCumProbList
            
            #print(origList, origCumProbList)
                
        randomDraw = random()
        sampledOrig = None
        
        for origID in range(0,len(origList)):
            if randomDraw <= origCumProbList[origID]:
                
                sampledOrig = origList[origID]
                break
            
        assert(sampledOrig is not None)
                
        return sampledOrig
   
    
    def sampleDestination(self, curStationName):
        
        if curStationName in self.destListDict.keys():
            destList = self.destListDict[curStationName]
            destCumProbList = self.destCumProbDict[curStationName]
        
        else:
            #generate set of all OD pairs
            odPairSet = set(self.odRatio.keys())
            
            cumProb = 0
            
            destList = list()
            destCumProbList = list()
            
            for odPair in odPairSet:
                if odPair[0] == curStationName:
                    destList.append( odPair[1] )
                    cumProb += self.odRatio[odPair]
                    destCumProbList.append( cumProb )
            
            self.destListDict[curStationName] = destList
            self.destCumProbDict[curStationName] = destCumProbList

                
        randomDraw = random()
        chosenDest = None
        
        for destID in range(0,len(destList)):
            if randomDraw <= destCumProbList[destID]:
                
                chosenDest = destList[destID]
                break
        
        assert(chosenDest is not None)
        
        return chosenDest
        
        
    
    def computeRatios(self):
        
        assert( self.corridorFlag == True )
        
        gamma = Parameter.relWeightODSplitFractions
        fracUB = Parameter.fracUtrechtBijlmer
        fracUA = Parameter.fracUtrechtAsdZ
        fracBA = Parameter.fracBijlmerAsdZ
                
        rU = self.ridershipTowards['Utrecht']
        #rB = self.ridershipTowards['Bijlmer']
        #rA = self.ridershipTowards['AsdZ']
        aU = self.numAlightings('Utrecht')
        bU = self.numBoardings('Utrecht')
        aB = self.numAlightings('Bijlmer')
        bB = self.numBoardings('Bijlmer')
        aA = self.numAlightings('AsdZ')
        bA = self.numBoardings('AsdZ')
        aS = self.numAlightings('Schiphol')
        bS = self.numBoardings('Schiphol')
        
        assert(bS == 0), \
            "Corridor trains terminate at Schiphol. No passengers expected to board at this station (currently %.2f)" % bS
        
        A = np.matrix([ \
                [1, 1, 1, 1, 0, 0, 0, 0, 0, 0], \
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
                [0, 1, 0, 0, 1, 0, 0, 0, 0, 0], \
                [0, 0, 1, 0, 0, 1, 0, 1, 0, 0], \
                [0, 0, 0, 1, 0, 0, 1, 0, 1, 1], \
                [0, 0, 0, 0, 1, 1, 1, 0, 0, 0], \
                [0, 0, 0, 0, 0, 0, 0, 1, 1, 0], \
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], \
                [0, 0, 0, 0, gamma*(1-fracUB), -gamma*fracUB, -gamma*fracUB, 0, 0, 0], \
                [0, 0, 0, 0, -gamma*fracUA, gamma*(1-fracUA), -gamma*fracUA, 0, 0, 0], \
                [0, 0, 0, 0, 0, 0, 0, gamma*(1-fracBA), -gamma*fracBA, 0] \
            ])
        
        b = [rU, aU, aB, aA, aS, bU, bB, bA, 0, 0, 0]
        
        x, rnorm = nnls(A, b)
        
        self.passODEst['upstream','Utrecht'] = x[0]
        self.passODEst['upstream','Bijlmer'] = x[1]
        self.passODEst['upstream','AsdZ'] = x[2]
        self.passODEst['upstream','Schiphol'] = x[3]
        self.passODEst['Utrecht','Bijlmer'] = x[4]
        self.passODEst['Utrecht','AsdZ'] = x[5]
        self.passODEst['Utrecht','Schiphol'] = x[6]
        self.passODEst['Bijlmer','AsdZ'] = x[7]
        self.passODEst['Bijlmer','Schiphol'] = x[8]
        self.passODEst['AsdZ','Schiphol'] = x[9]
        
        totBoardEst = dict()
        
        totBoardEst['upstream'] = self.passODEst['upstream','Utrecht'] +\
            self.passODEst['upstream','Bijlmer'] + self.passODEst['upstream','AsdZ'] + self.passODEst['upstream','Schiphol']
        totBoardEst['Utrecht'] = self.passODEst['Utrecht','Bijlmer'] +\
            self.passODEst['Utrecht','AsdZ'] + self.passODEst['Utrecht','Schiphol']
        totBoardEst['Bijlmer'] = self.passODEst['Bijlmer','AsdZ'] + self.passODEst['Bijlmer','Schiphol']
        totBoardEst['AsdZ'] = self.passODEst['AsdZ','Schiphol']
        
        self.odRatio['upstream','Utrecht'] = self.passODEst['upstream','Utrecht'] / totBoardEst['upstream']
        self.odRatio['upstream','Bijlmer'] = self.passODEst['upstream','Bijlmer'] / totBoardEst['upstream']
        self.odRatio['upstream','AsdZ'] = self.passODEst['upstream','AsdZ'] / totBoardEst['upstream']
        self.odRatio['upstream','Schiphol'] = self.passODEst['upstream','Schiphol'] / totBoardEst['upstream']
        self.odRatio['Utrecht','Bijlmer'] = self.passODEst['Utrecht','Bijlmer'] / totBoardEst['Utrecht']
        self.odRatio['Utrecht','AsdZ'] = self.passODEst['Utrecht','AsdZ'] / totBoardEst['Utrecht']
        self.odRatio['Utrecht','Schiphol'] = self.passODEst['Utrecht','Schiphol'] / totBoardEst['Utrecht']
        self.odRatio['Bijlmer','AsdZ'] = self.passODEst['Bijlmer','AsdZ'] / totBoardEst['Bijlmer']
        self.odRatio['Bijlmer','Schiphol'] = self.passODEst['Bijlmer','Schiphol'] / totBoardEst['Bijlmer']
        self.odRatio['AsdZ','Schiphol'] = 1
            
    def numBoardings(self, stationName):
        
        if ( (stationName == "upstream") and (self.corridorFlag==True) ):
            numBoard = self.ridershipTowards["Utrecht"]
            
        else:
            
            #assert( stationName in ( self.boardOutgoing.keys() | self.boardTransfer.keys() ) )
            
            numBoard = 0
            
            if stationName in self.boardOutgoing:
                numBoard += self.boardOutgoing[stationName]
                
            if stationName in self.boardTransfer:
                numBoard += self.boardTransfer[stationName]
        
        return numBoard
    
    def numAlightings(self, stationName):
        
        #assert( stationName in (self.alightIncoming.keys() | self.alightTransfer.keys() ) )
        
        numAlight = 0
        
        if stationName in self.alightIncoming:
            numAlight += self.alightIncoming[stationName]
            
        if stationName in self.alightTransfer:
            numAlight += self.alightTransfer[stationName]
            
        return numAlight
    
    def computeODRatios(self):
        
        servedStationNameSet = self.boardOutgoing.keys() | self.alightIncoming.keys() | \
            self.boardTransfer.keys() | self.alightTransfer.keys()
            
        if len(servedStationNameSet) == 4:
            #check notation
            assert ( servedStationNameSet == set(Parameter.stationNameDict.values()) )
            
            self.corridorFlag = True
            
            self.computeRatios()
            
        elif len(servedStationNameSet) == 1:
            stationNameSet = servedStationNameSet & set(Parameter.stationNameDict.values())
            assert( len( stationNameSet ) == 1 )
            uniqueStationName = stationNameSet.pop()
            
            self.odRatio['upstream',uniqueStationName] = 1
            self.odRatio[uniqueStationName,'downstream'] = 1
            
        else:
            stationNameSet = servedStationNameSet & set(Parameter.stationNameDict.values())
            assert( len( stationNameSet ) == len(servedStationNameSet) )
            
            if Parameter.showWarnings:
                print("Warning: Train partially serving corridor: %s" % stationNameSet)
            
            #trains serving two or three stations are only auxiliary. To keep things simple,
            #without impact on the system dynamics, assume that no passengers travel between the two stations.
            for stationName in stationNameSet:
                self.odRatio['upstream',stationName] = 1 #can be any positive number; has no influence in implemented population synthesis
                self.odRatio[stationName,'downstream'] = 1
             
        
    def __repr__(self):
        return "boardOutgoing: %s, alightIncoming: %s, boardTransfer: %s, alightTransfer: %s, ridershipTowards: %s, Corridor: %s\n totSynthBoard: %s, totSynthAlight: %s\nOD ratios: %s\nOD flows: %s" % \
            (self.boardOutgoing,self.alightIncoming,self.boardTransfer,self.alightTransfer, self.ridershipTowards, self.corridorFlag, self.totBoardSynthesized, self.totAlightSynthesized, self.odRatio, self.passODEst)
        
    def addRidershipTowards(self, stationName, numPass):
        assert(numPass >= 0), "train with invalid ridership (%s) to station %s" % (numPass,stationName)
        assert(stationName in Parameter.stationNameDict.values())
        
        if stationName not in self.ridershipTowards.keys():
            self.ridershipTowards[stationName] = 0
        
        self.ridershipTowards[stationName] += numPass
        
    def addBoardOutgoing(self, stationName, numPass):
        
        self.checkFeasibility(stationName, numPass)
        
        if stationName in self.boardOutgoing.keys():
            self.boardOutgoing[stationName] = self.boardOutgoing[stationName] + numPass
        else:
            self.boardOutgoing[stationName] = numPass
            
    def addAlightIncoming(self, stationName, numPass):
        
        self.checkFeasibility(stationName, numPass)
        
        if stationName in self.alightIncoming.keys():
            self.alightIncoming[stationName] = self.alightIncoming[stationName] + numPass
        else:
            self.alightIncoming[stationName] = numPass
            
           
    def addBoardTransfer(self, stationName, numPass):
        
        self.checkFeasibility(stationName, numPass)
        
        if stationName in self.boardTransfer.keys():
            self.boardTransfer[stationName] = self.boardTransfer[stationName] + numPass
        else:
            self.boardTransfer[stationName] = numPass    
            
    def addAlightTransfer(self, stationName, numPass):
        
        self.checkFeasibility(stationName, numPass)
        
        if stationName in self.alightTransfer.keys():
            self.alightTransfer[stationName] = self.alightTransfer[stationName] + numPass
        else:
            self.alightTransfer[stationName] = numPass
   
    
    def checkFeasibility(self, stationName, numPass):
        #check if station exists and number of travelers is strictly positive
        assert(stationName in Parameter.stationNameDict.values() )
        assert(numPass > 0)