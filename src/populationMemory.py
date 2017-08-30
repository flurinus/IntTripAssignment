from individualMemory import IndividualMemory

class PopulationMemory(object):


    def __init__(self, pedDictRaw, pedPaths):

        self.memoryDict = dict()
        
        for pedID in pedDictRaw.keys():
            self.memoryDict[pedID] = IndividualMemory()
            
        self.pathDict = dict(enumerate(pedPaths))
    
        #for each OD node, contains set of connecting paths
        self.odPathDict = dict()
        
        for pathID,nodeList in self.pathDict.items():
            
            origNode = nodeList[0]
            destNode = nodeList[-1]
            
            if (origNode,destNode) in self.odPathDict:
                self.odPathDict[(origNode,destNode)].add(pathID)
            else:
                self.odPathDict[(origNode,destNode)] = {pathID}
                
    def getPathSet(self,origNode,destNode,pedNet):
        
        if (origNode,destNode) in self.odPathDict:
            return self.odPathDict[origNode,destNode]
        else:
            shortestNodeList = pedNet.getShortestPath(origNode,destNode)
            pathID = len(self.pathDict) #pathIDs are simple enumerators
            pathIDSet = {pathID}
            
            self.pathDict[pathID] = shortestNodeList
            
            self.odPathDict[origNode,destNode] = pathIDSet
            
            #if Parameter.showWarnings:
            #    print("OD pair (%s,%s) not connected. Creating shortest path: %s" % (origNode,destNode,shortestNodeList))
            
            return pathIDSet
        
    def generatePathList(self):
        pathListLog = "Path list:\n"
        
        for pathID in range(0,len(self.pathDict)):
            pathListLog += "%d: %s\n" % (pathID,self.pathDict[pathID])
             
        return pathListLog
    
    def getLinkList(self,pathID,pedNet):
        
        nodeList = self.pathDict[pathID]
        
        linkList = list()
        
        for linkNum in range(0,len(nodeList)-1):
            upNode = nodeList[linkNum]
            downNode = nodeList[linkNum+1]
            
            linkID = pedNet.getLinkID(upNode,downNode)
            
            linkList.append(linkID)
        
        return linkList
    
    def resetAllPotentials(self):
        for memory in self.memoryDict.values():
            memory.invalidateEpisodePotentials()
    
    def resetExplorationSet(self):
        
        numEpisodesToExplore = 0
        
        for indMemory in self.memoryDict.values():
            numEpisodesToExplore += len(indMemory.episodesToExplore)
            indMemory.episodesToExplore.clear()
            
        return numEpisodesToExplore