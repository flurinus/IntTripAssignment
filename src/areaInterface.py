from parameter import Parameter


class AreaInterface:
    
    def __init__(self, flowCapacity):
        assert(flowCapacity > 0)
        
        self.flowCapacity = flowCapacity
        
        self.cumFlowThreshold = flowCapacity*Parameter.interfaceTimeInterval
        
        assert(self.cumFlowThreshold >= 1), \
            "Cumulative flow across interface must be larger than zero (current value: %.2f, flow capacity: %.2f, time interval: %.2f)" %\
            (self.cumFlowThreshold, flowCapacity, Parameter.interfaceTimeInterval)
                
        self.curFlowCapacity = self.cumFlowThreshold
        
        self.lastAnnouncementTime = 0
        
    def getWaitTime(self, simEnv):
        #compute wait time at interface to ensure respecting of flow capacity
        #Note: flow capacity is enforced in a relatively mild way
        
        curTime = simEnv.now
        
        #update flow capacity
        self.curFlowCapacity = min( self.cumFlowThreshold, \
            self.curFlowCapacity + (curTime - self.lastAnnouncementTime)*self.flowCapacity )
        
        waitTime = -1
        
        if 1 <= self.curFlowCapacity:
            waitTime = 0
        else:
            waitTime = (1 - self.curFlowCapacity)/self.flowCapacity
            
        #update remaining flow capacity and last passage time
        self.curFlowCapacity -= 1
        self.lastAnnouncementTime = curTime

        return waitTime
        
        
        
        