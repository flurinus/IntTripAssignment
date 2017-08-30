import math
import random
from parameter import Parameter 

class Stream:
    
    def __init__(self,edgeType,length,area):
        self.length = length
        self.area = area
        self.occupation = 0
        
        streamType = Parameter.densitySpeedRelationship[edgeType]
        
        self.basicFreeSpeed = streamType['basicFreeSpeed']
        self.gamma = streamType['shapeParam']
        self.jamDensity = streamType['jamDensity']
        
        assert(self.jamDensity >= area.maxDensity), \
            "The (potentially theoretical) jamDensity (%.2f) needs to be greater or equal the maximum allowed density (%.2f) to reduce the risk of grid-lock." %\
            (self.jamDensity,area.maxDensity)
        
        if 'walkProb' in streamType:
            self.walkingProbability = streamType['walkProb']
            self.mechSpeed = streamType['mechSpeed']
        else:
            self.walkingProbability = 1
        
        self.arrivalLogBook = [0]
        
    def getTravelTime(self,speedMultiplier):
        return self.length/self.getWalkingSpeed(speedMultiplier);
    
    def getWalkingSpeed(self,speedMultiplier):
        
        
        if ((1 == self.walkingProbability) or (random.random() <= self.walkingProbability)) :
            density = self.area.getAreaDensity()
            
            speed = self.basicFreeSpeed * speedMultiplier *(
                1 - math.exp(-self.gamma*(1/density - 1/self.jamDensity)) )
            
            #on escalators, minimum speed given by mechanical speed
            if self.walkingProbability < 1 and speed < self.mechSpeed:
                speed = self.mechSpeed
            
            
            if speed < Parameter.minSpeed:
                if Parameter.showWarnings:
                    speedWarning = "Low speed (%.2f) replaced by minSpeed (%.2f); speed multiplier %.2f; area of type %s, size %.2f, density %.2f" %\
                        (speed,Parameter.minSpeed,speedMultiplier, self.area.resource.areaType, self.area.resource.areaSize, density)
                     
                    print(speedWarning)
                
                speed = Parameter.minSpeed
            
        else:
            speed = self.mechSpeed
        
        assert(speed > 0), "speed (%.2f) invalid" % speed
                
        return speed
    
    def addPedestrian(self):
        self.occupation += 1
        
    def removePedestrian(self):
        assert(self.occupation>0)
        
        #remove pedestrian from area
        self.area.removePedestrian()
        
        #remove pedestrian from stream
        self.occupation -= 1
        
    def getArea(self):
        return self.area