from train import Train

class TransitSystem(object):

    def __init__(self, trainDictRaw, simEnv, pedNet, param):
        
        self.trainDict = dict()
                
        for trainName, train in trainDictRaw.items():
            platformSeq = train.platformSequence 
            arrTimeReal = train.arrTimeReal
            depTimeReal = train.depTimeReal
            arrTimeSched = train.arrTimeSched
            depTimeSched = train.depTimeSched
            rollingStockType = train.rollingStockType 
            numCars = train.numCars
            carSeatCap = train.carSeatCap 
            length = train.trainLength
                        
            self.trainDict[trainName] = Train(platformSeq, arrTimeReal, depTimeReal, arrTimeSched, depTimeSched,\
                rollingStockType, numCars, carSeatCap, length, simEnv, pedNet, param)    
            
    def addToSimulation(self, simEnv, pedNet):
                
        #initialize trains in simulation environment
        for curTrain in self.trainDict.values():
            simEnv.process(curTrain.propagate(simEnv,pedNet))
            
    def generateLog(self):
        
        log = ""
        
        for trainName, train in self.trainDict.items():
            
            log += "Train: %s\n" % trainName
            
            for (time, entry) in train.logBook:
                log += "%.2f: %s\n" % (time,entry)
                
            log += "\n"
        
        return log