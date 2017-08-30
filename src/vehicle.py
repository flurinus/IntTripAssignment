import simpy
import random
from parameter import Parameter

class Vehicle(object):

    def __init__(self, vehSeatCapacity, rollingStockType, simEnv):
        
        assert(vehSeatCapacity > 0), "vehSeatCapacity (%s) must be positive" % vehSeatCapacity
        
        self.doorServiceRateMean = Parameter.boardAlightServiceTimesPerVehicle[rollingStockType]
       
        self.rollingStockType=rollingStockType
        self.cabin = CabinResource(simEnv, vehSeatCapacity)
        self.door = simpy.PriorityResource(simEnv, capacity=1)
        
        #log book of ridership at arrival (before doors open)
        self.totalRidershipAtArrival = dict()
        self.auxiliaryRidershipAtArrival = dict()
        self.trackedRidershipAtArrival = dict()
        
    def logRidershipAtArrival(self, stationName):
        totalLoad = self.cabin.passengerLoad
        
        assert(stationName not in self.totalRidershipAtArrival.keys())
        assert(totalLoad >= 0)
        
        self.totalRidershipAtArrival[stationName] = totalLoad
        self.trackedRidershipAtArrival[stationName] = self.cabin.loadTrackedPassengers
        self.auxiliaryRidershipAtArrival[stationName] = self.cabin.loadAuxiliaryPassengers
        
    
    def requestBoarding(self):
        #request door with low priority
        #randomize boarding order by assigning random positive priority
        return self.door.request(priority=random.random())
    
    def requestAlighting(self):
        #request door with high priority
        #randomize boarding order by assigning random negative priority
        return self.door.request(priority=-random.random())
    
    def boardServTime(self):
        return random.expovariate(1/self.doorServiceRateMean)
    
    def alightServTime(self):
        return random.expovariate(1/self.doorServiceRateMean)

    def getRidingCostSeated(self,timeStart,timeEnd):
        assert (timeStart in self.cabin.cumSeatedCost)
        assert (timeEnd in self.cabin.cumSeatedCost)
        return self.cabin.cumSeatedCost[timeEnd] - self.cabin.cumSeatedCost[timeStart]
    
    def getRidingCostStanding(self,timeStart,timeEnd):
        assert (timeStart in self.cabin.cumStandingCost), \
            "timeStart: %.2f not in cabin.cumStandingCost: %s" % (timeStart,self.cabin.cumStandingCost)
        assert (timeEnd in self.cabin.cumStandingCost), \
            "timeEnd: %.2f not in cabin.cumStandingCost: %s" % (timeEnd,self.cabin.cumStandingCost)
        return self.cabin.cumStandingCost[timeEnd] - self.cabin.cumStandingCost[timeStart]
    
#patch resource class to keep information on travel cost
class CabinResource(simpy.Resource):
    def __init__(self, simEnv,capacity):
        super().__init__(simEnv,capacity)  
        
        #cumulative walking and waiting cost
        self.cumStandingCost = {0:0}
        self.cumSeatedCost = {0:0}
        
        #total passenger load, including standing passengers
        self.passengerLoad = 0
        
        #separate reporting for corridor and auxiliary passengers
        self.loadTrackedPassengers = 0
        self.loadAuxiliaryPassengers = 0
        
        #density
        self.loadFactorLog = {0:0}
        
        self.lastTime = 0

    def request(self, *args, **kwargs):
        self.updateCost()
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.updateCost()
        return super().release(*args, **kwargs)
    
    def updateCost(self):
        
        curTime = self._env.now
        
        if curTime != self.lastTime:        
            lastStandingCost = self.cumStandingCost[self.lastTime]
            lastSeatedCost = self.cumSeatedCost[self.lastTime]
            
            curTime = self._env.now
            
            if not curTime == 0:
                assert(curTime != self.lastTime)
            
            curLoadFactor = self.passengerLoad/self.capacity
            
            self.loadFactorLog[curTime] = curLoadFactor
            
            curStandingCost = lastStandingCost + self.standingVOT(curLoadFactor)*(curTime - self.lastTime)
            curSeatedCost = lastSeatedCost + self.seatedVOT(curLoadFactor)*(curTime - self.lastTime)
                    
            self.cumStandingCost[curTime] = curStandingCost
            self.cumSeatedCost[curTime] = curSeatedCost
            
            self.lastTime = curTime
        
    def standingVOT(self,loadFactor):
        baseCostIVT = Parameter.betaIVTZero
        timeMultiplier = self.getStandingLOSMultiplier(loadFactor)
        
        return baseCostIVT*timeMultiplier
    
    def seatedVOT(self,loadFactor):
        baseCostIVT = Parameter.betaIVTZero
        timeMultiplier = self.getSeatedLOSMultiplier(loadFactor)
        
        return baseCostIVT*timeMultiplier
    
    def getStandingLOSMultiplier(self,loadFactor):
        for loadFactorThreshold in Parameter.loadFactorThresholdsStanding:
            if loadFactor <= loadFactorThreshold:
                return Parameter.timeMultiplierIVTStanding[loadFactorThreshold]
        
    def getSeatedLOSMultiplier(self,loadFactor):
        for loadFactorThreshold in Parameter.loadFactorThresholdsSeated:
            if loadFactor <= loadFactorThreshold:
                return Parameter.timeMultiplierIVTSeated[loadFactorThreshold]