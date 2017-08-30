import simpy
import math
import numpy as np
from parameter import Parameter

class Area:
    
    def __init__(self, simEnv, surfaceArea, areaType):
        assert(surfaceArea > 0)
        assert(areaType in Parameter.maxFacilityDensity)
        
        self.streamList = list()
        
        #area type
        self.areaType = areaType
        
        #capacity
        self.maxDensity = Parameter.maxFacilityDensity[areaType]['maxDensity']
        maxNumPed = math.floor( surfaceArea * self.maxDensity )
                
        self.resource = AreaResource(simEnv,maxNumPed,surfaceArea,areaType)
        
    def addStream(self, linkID):
        self.streamList.append(linkID)
            
    #returns resource request event
    def getResReqEvent(self):
        return self.resource.request()
    
    def getRelease(self,resReqEvent):
        self.resource.release(resReqEvent)
        
    def getAreaDensity(self):
        return self.resource.count/self.resource.areaSize
    
    def getWalkingCost(self,timeIn, timeOut):
        if timeIn not in self.resource.cumWalkCost or timeOut not in self.resource.cumWalkCost:
            print("self.resource.cumWalkCost", self.resource.cumWalkCost)
            print("timeIn: %.3f, timeOut: %.3f" % (timeIn, timeOut))
        
        assert (timeIn in self.resource.cumWalkCost)
        assert (timeOut in self.resource.cumWalkCost)
        return self.resource.cumWalkCost[timeOut] - self.resource.cumWalkCost[timeIn]
    
    def getWaitingCost(self,timeIn, timeOut):
        assert (timeIn in self.resource.cumWaitCost and timeOut in self.resource.cumWaitCost)
        return self.resource.cumWaitCost[timeOut] - self.resource.cumWaitCost[timeIn] 
    
#patch resource class to keep information on travel cost
class AreaResource(simpy.Resource):
    def __init__(self, simEnv,capacity,areaSize,areaType):
        super().__init__(simEnv,capacity)
        
        self.areaSize = areaSize
        self.areaType = areaType
        
        #cumulative walking cost
        self.cumWalkCost = {0:0}
        
        #on platform areas, people may also wait
        if self.areaType == "horizontal":
            self.cumWaitCost = {0:0}
        
        #density
        self.densityLog = {0:0}
        
        self.lastTime = 0

    def request(self, *args, **kwargs):
        self.updateCost()
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.updateCost()
        return super().release(*args, **kwargs)
    
    def updateCost(self):
        
        curTime = self._env.now
        
        #add time stamp only if different from previous
        if curTime != self.lastTime:
            curDensity = self.count/self.areaSize
            self.densityLog[curTime] = curDensity
            
            lastWalkCost = self.cumWalkCost[self.lastTime]
            curWalkCost = lastWalkCost + self.walkingVOT(curDensity)*(curTime - self.lastTime)
            self.cumWalkCost[curTime] = curWalkCost
            
            #compute waiting cost if needed
            if self.areaType == "horizontal":
                lastWaitCost = self.cumWaitCost[self.lastTime]
                curWaitCost = lastWaitCost + self.waitingVOT(curDensity)*(curTime - self.lastTime)
                self.cumWaitCost[curTime] = curWaitCost
                
            self.lastTime = curTime
        
    def walkingVOT(self,density):
        if self.areaType == "horizontal":
            activity = "walkingHorizontal"
        else:
            #for escalators and stairways, activity pre-determined by facility type
            activity = self.areaType
        
        assert(activity in Parameter.timeMultiplierRailAccess), \
            "activity '%s' not in Parameter.timeMultiplierRailAccess" % activity
        
        return self.getRailAccessTimeMultiplier(activity, density)*Parameter.betaIVTZero
    
    def waitingVOT(self,density):
        assert(self.areaType == "horizontal"), "Pedestrian erroneously waiting on %s" % self.areaType
        activity = "waitingPlatform"
        assert(activity in Parameter.timeMultiplierRailAccess)
        
        return self.getRailAccessTimeMultiplier(activity, density)*Parameter.betaIVTZero
    
    def getRailAccessTimeMultiplier(self, activity, density):
        assert( activity in Parameter.timeMultiplierRailAccess ), \
            "activity '%s' not in Parameter.timeMultiplierRailAccess" % activity
        
        #retrieve crowding multiplier
        densCrowdMultTupleList = Parameter.timeMultiplierRailAccess[activity]
        densList, crowdMultList = zip(*densCrowdMultTupleList)
        
        assert( min(densList) <= density and density <= max(densList) )
        return np.interp(density, densList, crowdMultList)
    
    #def getWalkingLOSMultiplier(self,density):
    #    for index,losThreshold in enumerate(Parameter.losWalkingFruin):
    #        if density <= losThreshold:
    #            losLevel = Parameter.losLevels[index]
    #            break
    #            
    #    #get multiplier corresponding to current walking LOS 
    #    return Parameter.crowdingMultiplierLOS[losLevel]
    
    #def getWaitingLOSMultiplier(self,density):
    #    for index,losThreshold in enumerate(Parameter.losWaitingFruin):
    #        if density <= losThreshold:
    #            losLevel = Parameter.losLevels[index]
    #            break
    #    
    #    #get multiplier corresponding to current walking LOS 
    #    return Parameter.crowdingMultiplierLOS[losLevel]
        
        
        
        