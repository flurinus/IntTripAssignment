from random import random

class RocktGateLine(object):

    def __init__(self):
        self.entranceGateList = None
        self.entranceGateUsageFreq = dict()
        self.entranceGateUsageTimeDist = dict()
        self.entranceCumProbList = None
        
        self.exitGateList = None
        self.exitGateUsageFreq = dict()
        self.exitGateUsageTimeDist = dict()
        self.exitCumProbList = None
        
    def __repr__(self):        
        return ("entrance: %s, exit: %s" % (self.entranceGateUsageFreq, self.exitGateUsageFreq) )
    
    def addEntranceUsage(self, gateNode, entranceTime, numTravelers):
        
        if gateNode not in self.entranceGateUsageFreq.keys():
            self.entranceGateUsageFreq[gateNode] = 0
            
        if (gateNode, entranceTime) not in self.entranceGateUsageTimeDist.keys():
            self.entranceGateUsageTimeDist[gateNode, entranceTime] = 0
        
        self.entranceGateUsageFreq[gateNode] += numTravelers
        self.entranceGateUsageTimeDist[gateNode, entranceTime] += numTravelers
    
    def addExitUsage(self, gateNode, exitTime, numTravelers):
        
        if gateNode not in self.exitGateUsageFreq.keys():
            self.exitGateUsageFreq[gateNode] = 0
        
        if (gateNode, exitTime) not in self.exitGateUsageTimeDist.keys():
            self.exitGateUsageTimeDist[gateNode, exitTime] = 0
        
        self.exitGateUsageFreq[gateNode] += numTravelers
        self.exitGateUsageTimeDist[gateNode, exitTime] += numTravelers
    
    
    def drawEntranceTime(self, entranceNode):
        
        entrTimeList = list()
        cumFreqList = list()
        totFreq = 0
        
        for key, numTrav in self.entranceGateUsageTimeDist.items():
            
            curEntrNode, curEntrTime = key
            
            if (entranceNode == curEntrNode):
                entrTimeList.append(curEntrTime)
                totFreq += numTrav
                cumFreqList.append(totFreq)
                
        randomDraw = totFreq*random()
        
        #print("entrTimeList: %s" % entrTimeList)
        #print("cumFreqList: %s" % cumFreqList)
        #print("randomDraw: %.2f, totFreq: %.2f" % (randomDraw, totFreq) )
        
        for timeID in range(0,len(entrTimeList)):
            if randomDraw <= cumFreqList[timeID]:
                entranceTime = entrTimeList[timeID]
                break 
        
        #print("sampledEntranceTime: %d" % entranceTime )
        
        assert(entranceTime >= 0), "Non-negative entrance time (%s)" % entranceTime
        
        return entranceTime
        
            
        
    
    def drawEntranceGate(self):
        
        if self.entranceGateList is None:
            totUsage = 0
            
            self.entranceGateList = list()
            cumUsageList = list()
            self.entranceCumProbList = list()
            
            for gate, usage in self.entranceGateUsageFreq.items():
                self.entranceGateList.append(gate)
                
                totUsage += usage
                cumUsageList.append(totUsage)
                
            for cumUsage in cumUsageList:
                self.entranceCumProbList.append(cumUsage/totUsage)
            
        randomDraw = random()
        entranceGate = None
        
        for gateID in range(0,len(self.entranceGateList)):
            if randomDraw <= self.entranceCumProbList[gateID]:
                
                entranceGate = self.entranceGateList[gateID]
                break
            
        assert(entranceGate is not None)
                
        return entranceGate

    def drawExitGate(self):
        
        if self.exitGateList is None:
            totUsage = 0
            
            self.exitGateList = list()
            cumUsageList = list()
            self.exitCumProbList = list()
            
            for gate, usage in self.exitGateUsageFreq.items():
                self.exitGateList.append(gate)
                
                totUsage += usage
                cumUsageList.append(totUsage)
                
            for cumUsage in cumUsageList:
                self.exitCumProbList.append(cumUsage/totUsage)
            
        randomDraw = random()
        exitGate = None
        
        for gateID in range(0,len(self.exitGateList)):
            if randomDraw <= self.exitCumProbList[gateID]:
                
                exitGate = self.exitGateList[gateID]
                break
            
        assert(exitGate is not None)
                
        return exitGate

            
        