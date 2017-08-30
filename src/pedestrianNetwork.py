from station import Station
from area import Area
from stream import Stream
import networkx as nx
import matplotlib.pyplot as plt
from trainPlatform import TrainPlatform
from parameter import Parameter
from areaInterface import AreaInterface

class PedestrianNetwork:
    
    def __init__(self, nodeList, streamList, stationList, areaList, interfaceList, platformAttributeDict, simEnv):
        #add nodes and edges separately
        #check existence of nodes when adding edges
        #an edge is characterized by an origin, destination, and is associated with a unique ID
        #a stream is characterized by a length, an associated area, and the corresponding edgeID
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(nodeList)
        
        #generate stations
        self.stationDict = dict()
        
        
        for stationName in stationList:
            self.stationDict[stationName] = Station()
        
        #generate areas
        self.areaDict = dict()
        self.areaStationDict = dict()
        
        for (areaName, areaSize, areaType, stationName) in areaList:
            assert(stationName in self.stationDict), "stationName '%s' not in stationDict" % stationName
            assert(areaName not in self.areaDict), "areaName '%s' not in areaDict" % areaName
            
            self.areaStationDict[areaName] = stationName
            
            self.areaDict[areaName] = Area(simEnv, areaSize, areaType)
        
        
        #generate network (nodes, links)
        self.streamDict = dict()
        self.streamIDDict = dict()
        self.streamIDDictRev = dict()
        self.linkIDAreaIDDict = dict()
        
        for (linkID, (origNode, destNode, length, areaID, edgeType) ) in enumerate(streamList):
            
            assert(edgeType in Parameter.densitySpeedRelationship)
            
            if (edgeType == 'bidirWalkway'):
                bidir = True
                linkIDrev = linkID + len(streamList)
            else:
                bidir = False
            
            #check if origin and destination node exist in nodelist
            assert( self.graph.has_node(origNode) ), "origNode (%s) does not exist" % origNode
            assert( self.graph.has_node(destNode) ), "destNode (%s) does not exist" % destNode
            
            #generate link, characterized by origin and destination node, and free-flow travel time (for route choice)
            freeTravelTime = length/Parameter.densitySpeedRelationship[edgeType]['basicFreeSpeed']
            
            self.graph.add_edge(origNode, destNode, freeFlowTraversalTime = freeTravelTime)
            if bidir:
                self.graph.add_edge(destNode,origNode, freeFlowTraversalTime = freeTravelTime)
            
            #corresponding area
            area = self.areaDict[areaID]
            
            #check compatibility of area and edge
            assert(area.areaType == Parameter.edgeAreaType[edgeType])
            
            #add link to area
            assert (areaID in self.areaDict) #check if area exists in areaDict
            area.addStream(linkID)
            if bidir:
                area.addStream(linkIDrev)
            
            #add link and area ID to linkIDAreaIDDict
            self.linkIDAreaIDDict[linkID] = areaID
            if bidir:
                self.linkIDAreaIDDict[linkIDrev] = areaID
            
            
            #generate stream, characterized by type, length and area, and associated with a link
            self.streamDict[linkID] = Stream(edgeType, length, area)
            if bidir:
                self.streamDict[linkIDrev] = Stream(edgeType, length, area)
            
            #generate streamID lookup table
            self.streamIDDict[linkID] = (origNode,destNode)
            self.streamIDDictRev[(origNode,destNode)] = linkID
            if bidir:
                self.streamIDDict[linkIDrev] = (destNode,origNode)
                self.streamIDDictRev[(destNode,origNode)] = linkIDrev
        
        self.computeShortestPath()
        
        #add interfaces
        self.interfaceDict = dict()
        self.interfaceIDDict = dict()
        
        for (interfaceID, (areaNameOne, areaNameTwo, flowCapacity)) in enumerate(interfaceList):
            self.interfaceIDDict[(areaNameOne,areaNameTwo)] = interfaceID
            self.interfaceIDDict[(areaNameTwo,areaNameOne)] = interfaceID
            
            self.interfaceDict[interfaceID] = AreaInterface(flowCapacity)
        
        if Parameter.showWarnings:
            #contains interfaces for which no flow capacity has been set    
            self.interfaceDebugSet = set()
                
        #add platforms
        self.platformDict = dict()
        self.boardingLinkPlatformDict = dict()
        self.platformStationDict = dict()
        
        #read platforms
        areaLimitCoord = platformAttributeDict['areaLimits']
        
        for platformID in platformAttributeDict['platformNames']:
            
            trainInterfaceNodes = platformAttributeDict['interfaceNodes'][platformID]
            stopSignalPos = platformAttributeDict['stopSignalPos'][platformID]
            usageDirection = platformAttributeDict['usageDirection'][platformID]
            
            stopPosSet = set(stopSignalPos.values())
            assert(len(stopPosSet) > 1 or min(stopPosSet) > 0 or platformID == Parameter.upstreamPlatform or platformID == Parameter.downstreamPlatform), \
                "Provided stop positions for %s seem invalid %s" % (platformID, stopSignalPos)
            
            curPlatform = TrainPlatform(trainInterfaceNodes, areaLimitCoord, stopSignalPos, usageDirection, \
                self.streamIDDict,self.streamIDDictRev,self.linkIDAreaIDDict,self.areaStationDict,self.graph)
            
            self.platformDict[platformID] = curPlatform
            
            stationName = curPlatform.stationName
            self.stationDict[stationName].platformNameSet.add(platformID)
            self.platformStationDict[platformID] = stationName
            
            #store boarding links in global dict            
            for boardLinkID in curPlatform.boardLinkIDSet:
                #any boarding link at most affiliated with a single platform
                assert(boardLinkID not in self.boardingLinkPlatformDict)
                            
                self.boardingLinkPlatformDict[boardLinkID] = platformID
                
             
    def computeShortestPath(self):
        self.shortestPath = nx.shortest_path(self.graph,weight='freeFlowTraversalTime')
        
    def getShortestPath(self, origNode, destNode):
        assert(self.shortestPath), "shortest path needs to be computed first"
        
        return self.shortestPath[origNode][destNode]
    
    def getLinkNodes(self, linkID):
        return self.streamIDDict[linkID]
    
    def getLinkOrigNode(self, linkID):     
        return self.streamIDDict[linkID][0]
    
    def getLinkDestNode(self, linkID):        
        assert(linkID in self.streamIDDict.keys()), \
            "linkID %s not in streamIDDict: %s" % (linkID, self.streamIDDict)
             
        return self.streamIDDict[linkID][1]
    
    def getLinkID(self, origNode, destNode):
        return self.streamIDDictRev[(origNode,destNode)]
    
    def getInterfaceID(self,areaNameOne,areaNameTwo):
        
        if (areaNameOne,areaNameTwo) in self.interfaceIDDict.keys():
            return self.interfaceIDDict[(areaNameOne,areaNameTwo)]
        else:
            return None
        
    def getInterface(self, interfaceID):
        
        assert(interfaceID in self.interfaceDict), \
            "InterfaceID %s not in list of interfaceIDs %s" % (interfaceID, self.interfaceIDDict)
        
        return self.interfaceDict[interfaceID]
            
    
    def getPlatformName(self, linkID):
        if (linkID in self.linkIDAreaIDDict):
            areaName = self.linkIDAreaIDDict[linkID]
            return self.platformAreaDict[areaName]
        
        else:
            return False
    
    def getStream(self, linkID):
        return self.streamDict[linkID]
    
    def getArea(self, areaID):
        return self.areaDict[areaID]
    
    def getAreaFromLinkID(self, linkID):
        return self.getStream(linkID).getArea()
    
    def getAreaIDFromLinkID(self, linkID):
        return self.linkIDAreaIDDict[linkID]
            
    def generateGraph(self,fileName):
        nx.draw(self.graph, with_labels = True)
        plt.savefig(fileName)