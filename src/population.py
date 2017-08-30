from pedestrian import Pedestrian

class Population(object):

    def __init__(self, travPop, pedNet, transSys, popExp, param):
    
        self.pedestrianDict = dict()
        
        for pedID, rawPed in travPop.items():
            persMem = popExp.memoryDict[pedID]
            
            origNode = rawPed.origNode
            destNode = rawPed.destNode
            
            transferStation = rawPed.transferStation
                    
            depTime = rawPed.depTime
            assert(depTime >= 0), "traveler %s has negative depTime (%s) %s" % (pedID, depTime, travPop[pedID])
            
            trainList = rawPed.trainList
            
            self.pedestrianDict[pedID] = Pedestrian(origNode, destNode, depTime, trainList, transferStation, pedNet, transSys, persMem, param)
                   
    def addToSimulation(self, simEnv, pedNet, trainList, popMemory):

        #initialize pedestrians in queueing pedestrianNetwork
        for curPed in self.pedestrianDict.values():
            simEnv.process(curPed.propagate(simEnv, pedNet, trainList, popMemory))
            
    def generateLog(self):
        
        log = ""
        
        for pedName, ped in self.pedestrianDict.items():
                        
            log += "Traveler: %s\n" % pedName
            
            log += "Total travel utility: %.2f (%.2f)\n" % (ped.getRelevantTravelCost(), ped.totalTravelUtility)
            
            #note: the walking, waiting and riding utility do NOT sum up to the total travel utility,
            #as they do not take into account penalties for transfers or missed trains (also first train is considered as transfer)
            log += "Walking utility: %.2f; Waiting utility: %.2f, Riding utility: %.2f, Penalties: %.2f\n" % \
                        (ped.totalWalkUtility, ped.totalWaitUtility, ped.totalRideUtility, ped.totalPenalty)
            
            log += "speed multiplier : %.3f\n" % ped.personalMemory.speedMultiplier
            
            log += "Activity sequence: "
            for activityID in range(0,len(ped.activitySequence)):
                activity = ped.activitySequence[activityID]
                log += activity.actType
                if activityID < len(ped.activitySequence)-1:
                    log += " - "
                else:
                    log += "\n"
            
            for (time, entry) in ped.logBook:
                log += "%.2f: %s\n" % (time,entry)
                
            log += "\n"
             
            log += "Episode list: "
            log += str(ped.episodeIDList)
            
            log += "\n\n"
            
            log += "Accumulated memory:\n"
            
            log += str(ped.personalMemory)
            
            log += "\n\n"
                
        return log
            

    def getTotTravDisutility(self):
        totalCost = 0
        numPed = 0
        
        for curPed in self.pedestrianDict.values():
            pedCost = curPed.getRelevantTravelCost()
            
            assert(pedCost <= 0)
            
            if pedCost < 0:
                numPed += 1
                
            totalCost += pedCost
        
        return totalCost, numPed
                    
        
            
        
        