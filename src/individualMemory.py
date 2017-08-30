from parameter import Parameter
from episode import Episode
import numpy.random as rnd

class IndividualMemory(object):

    def __init__(self):
        
        self.episodeDict = dict()
        
        #draw free-flow speed multiplier
#         rnd.seed( struct.unpack('I', open("/dev/random","rb").read(4) )[0] )
        rnd.seed()
        self.speedMultiplier = rnd.normal(1,Parameter.freeFlowSpeedSigma)
        while (self.speedMultiplier <= 0):
            if Parameter.showWarnings:
                print("Warning: Negative speed-multiplier (%s) resampled." % self.speedMultiplier)
            self.speedMultiplier = rnd.normal(1,Parameter.freeFlowSpeedSigma)
        
        #binary flag equaling True if all available episodes have been explored, False otherwise
        #has to be reset in every learning instance
        self.episodesToExplore = set()
                
    def __repr__(self):
        memStr = ""
        
        sortedEpisodeList = sorted(self.episodeDict.keys(), key=lambda tup: (tup[0],tup[1]) )
        
        
        for episodeID in sortedEpisodeList:
            episode = self.episodeDict[episodeID]
            
            memStr += "Episode " + str(episodeID) + ":\n"
        
            memStr += "utility: " + str(episode.cost) + "\n"
            memStr += "potential: " + str(episode.getPotential(self.episodeDict,None)) + "\n"
            #memStr += "prevEpisodeSet: " + str(episode.prevEpisodeSet) + "\n"
            memStr += "nextEpisodeDict: " + str(episode.nextEpisodeDict) + "\n"
            
            memStr += "\n"
        
        return memStr
    
    def getPathPotential(self,actNum,pathID):
        
        episodeID = (actNum,pathID)
        
        if episodeID not in self.episodeDict:
            #notify learning instance of required additional exploration
            self.requireExploration(episodeID)
            
            #assume arbitrary large potential to make pedestrian explore new episodes
            return Parameter.initialPotential
        else:
            return self.episodeDict[actNum,pathID].getPotential(self.episodeDict,self)
        
    def initializeEpisode(self,episodeID):
        
        if episodeID not in self.episodeDict:
            self.episodeDict[episodeID] = Episode()            
    
    def memorizeEpisode(self,episodeID,episodeUtility):
        
        assert(episodeID in self.episodeDict)
        
        assert(episodeUtility <= 0) #travel utility always negative, since utility = -cost
        
        if 0 == self.episodeDict[episodeID].cost:
            self.episodeDict[episodeID].cost = episodeUtility
        else:
            assert(0< Parameter.learningParam < 1)
            self.episodeDict[episodeID].cost = Parameter.learningParam * episodeUtility + (1-Parameter.learningParam) * self.episodeDict[episodeID].cost

    #invalidate episode potentials to force recursive updating
    def invalidateEpisodePotentials(self):
            for episode in self.episodeDict.values():
                episode.precomputedPotential = None
                
    def requireExploration(self, episodeID):
        self.episodesToExplore.add(episodeID)
                
                
#     def getExpPathUtility(self,pathID):
#         if pathID in self.pathUtilDict:
#             expUtility = math.exp(self.pathUtilDict[pathID])
#         else:
#             expUtility = 1
#         
#         #note: utilities represent cost and should be finite and negative!
#         assert(0 < expUtility <= 1)
#         
#         return expUtility
#     
#     def getExpBoardLinkUtility(self,boardLinkID):
#         if boardLinkID in self.boardLinkUtilDict:
#             expUtility = math.exp(self.boardLinkUtilDict[boardLinkID])
#         else:
#             expUtility = 1
#         
#         #note: utilities represent cost and should be finite and negative!
#         assert(0 < expUtility <= 1)
#         
#         return expUtility
#     
#     def memorizePathUtil(self,pathID,pathCost):
#         
#         if pathID not in self.pathUtilDict:
#             self.pathUtilDict[pathID] = pathCost
#         else:
#             assert(0< Parameter.learningParam < 1)
#             self.pathUtilDict[pathID] = Parameter.learningParam * pathCost + (1-Parameter.learningParam) * self.pathUtilDict[pathID]
# 
#     def memorizeBoardLinkUtil(self,boardLinkID,boardLinkCost):
#         
#         if boardLinkID not in self.boardLinkUtilDict:
#             self.boardLinkUtilDict[boardLinkID] = boardLinkCost
#         else:
#             assert(0< Parameter.learningParam < 1)
#             self.boardLinkUtilDict[boardLinkID] = Parameter.learningParam * boardLinkCost + (1-Parameter.learningParam) * self.boardLinkUtilDict[boardLinkID]
