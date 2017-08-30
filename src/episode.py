import math
from parameter import Parameter
class Episode(object):
    

    def __init__(self):
        
        self.cost = 0
        #self.nextEpisodeSet = set()
        
        #next episode dict: keys represent episode IDs, values probability of availability
        #most episodes (e.g. routes) are always available (probability = 1)
        #specific vehicles are only partially available, as the boarding link->vehicle ID
        #assignment is random
        self.nextEpisodeDict = dict()
        
        self.precomputedPotential = None
            
        
    #def updatePotential(self):
    #    pass
        #potential = ln(sum exp(pathCost) potential_downstreamNode)
        #=pathCost + ln(sum potential_downstreamNode)
        
    def getPotential(self,episodeDict,persMemory):
        
        if self.precomputedPotential is not None:
            pass
        if len(self.nextEpisodeDict) > 0:
                        
            potential = 0
            for nextEpisodeID, nextEpisodeAvailProb in self.nextEpisodeDict.items():
                if nextEpisodeID in episodeDict:
                    potential += nextEpisodeAvailProb*episodeDict[nextEpisodeID].getPotential(episodeDict,persMemory)
                else:
                    #during printing, no learning instance required to be updated
                    if not persMemory == None:
                        #notify learning instance of required additional exploration
                        persMemory.requireExploration(nextEpisodeID)
                    
                    potential += nextEpisodeAvailProb*Parameter.initialPotential
                
            self.precomputedPotential = math.exp(self.cost) * potential
            
            assert(potential>0), "potential must be strictly positive: %s, cost: %s" % (self.nextEpisodeDict, self.cost)
            
        else:
            self.precomputedPotential = math.exp(self.cost) * Parameter.initialPotential
            
            assert(self.precomputedPotential > 0), "invalid cost %s" % self.cost
        
        return self.precomputedPotential