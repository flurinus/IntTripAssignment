from parameter import Parameter
from methodLibrary import weightedChoice


class RocktTraveler(object):

    def __init__(self, origNode, destNode, depTime, trainList, transferStation=None):
        
        assert( (origNode is not None) and (destNode is not None) and (depTime is not None) ),\
            "%s (%.2f) to %s" % (origNode, depTime, destNode)
        
        #recover or resample faulty gate IDs
        if origNode not in Parameter.rocktGateIDSetIn:
            if origNode in Parameter.rocktGateIDCorrectionDict.keys():
                origNode = Parameter.rocktGateIDCorrectionDict[origNode]
            elif origNode in Parameter.utrechtCorruptedGateIDs:
                origNode = weightedChoice(Parameter.utrechtGateFrequencyDict)
                
        if origNode in Parameter.rocktInGateResampleDict.keys():
            sampleGateDict = Parameter.rocktInGateResampleDict[origNode]
            origNode = weightedChoice(sampleGateDict)
        
        assert(origNode in Parameter.rocktGateIDSetIn), "origNode (%s) invalid" % origNode
            
        #recover or resample faulty gate IDs
        if destNode not in Parameter.rocktGateIDSetOut:
            if destNode in Parameter.rocktGateIDCorrectionDict.keys():
                destNode = Parameter.rocktGateIDCorrectionDict[destNode]
            elif destNode in Parameter.utrechtCorruptedGateIDs:
                destNode = weightedChoice(Parameter.utrechtGateFrequencyDict)
        assert(destNode in Parameter.rocktGateIDSetOut), "destNode (%s) invalid" % destNode
                        
        self.origNode = 'G' + str(origNode) #append NS gate node names by G
        self.destNode = 'G' + str(destNode) #append NS gate node names by G
        
        self.depTime = float(depTime) #check if departure time is numeric
        assert(depTime >= 0), "negative depTime not allowed (%s)" % depTime
        
        self.transferStation = transferStation
        
        if isinstance(trainList, int):
            self.trainList = list()
            self.trainList.append(trainList)
        elif isinstance(trainList, list):
            self.trainList = trainList
        else:
            print("Warning: Could not read trainList.")
        
    def setTransferStation(self, transferStationName):
        self.transferStation = transferStationName
        
    def __repr__(self):        
        return ( "passenger from %s to %s, leaving at %d, taking train(s) %s, transferring at: %s" % \
            (self.origNode, self.destNode, self.depTime, self.trainList, self.transferStation) )    