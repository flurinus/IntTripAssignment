import time
from parameter import Parameter
from populationMemory import PopulationMemory
from learningInstance import LearningInstance

class SimulationRun(object):

    def __init__(self,nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop,pedPaths,param,runID):
        
        popMemory = PopulationMemory(travPop,pedPaths) 
        
        timeStart = time.time()
        
        self.simOutputSet = set()

        for instanceID in range(0,Parameter.learningInstances+Parameter.finalInstances):
            
            print("%d: %d/%d started (time elapsed: %.2f)" % (runID+1, instanceID+1, Parameter.learningInstances+Parameter.finalInstances, time.time()-timeStart))
            
            #perform learning instances
            if instanceID < Parameter.learningInstances:
                LearningInstance(nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop,popMemory,param,runID,instanceID)
            
            #perform and store final instances
            else:
                finalInstance = LearningInstance(nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop,popMemory,param,runID,instanceID)
                self.simOutputSet.add(finalInstance.simOutput)
                
                #outputQueue.put(finalInstance.simOutput)