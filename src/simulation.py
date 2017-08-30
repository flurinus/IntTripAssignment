from multiprocessing import Pool
from simulationRun import SimulationRun
from parameter import Parameter
from methodLibrary import saveObject
import sys
#from simulationOutput import SimulationOutput


class Simulation(object):

    def __init__(self, nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPopRaw,pedPaths,param):
        
        assert(Parameter.numSimRuns > 0)
        
        #stores the output of individual simulation runs (final learning instance)
        #ordered randomly
        #outputQueue = Queue()
        self.resultSet = set()
        
        if (Parameter.numSimRuns == 1):
            print("Synthesizing traveler population: ", end='')
            travPop = travPopRaw.synthesizeTravelPopulation()
            print("%d pass" % len(travPop))
            
            simOutputSet = self.worker(nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop,pedPaths,param,runID=0)
            self.resultSet |= simOutputSet
                        
        else:
            #synthesize traveler population            
            travPop = dict()
            
            print("Synthesizing traveler population: ", end='')
            
            for runID in range(Parameter.numSimRuns):
                travPop[runID] = travPopRaw.synthesizeTravelPopulation()
                
                print("runID %d (%d pass)" % (runID+1,len(travPop[runID])), end=', ', flush=True)
                
                travelerInputFile = open(param.outputFolder + "/travList_run%d.txt" % runID, 'w')
                travelerInputFile.write(str(travPop[runID]))
                travelerInputFile.close()
                
            print("done.")
                        
            pool = Pool(processes = Parameter.numParallelRuns)
            
            argList = list()
            
            for runID in range(Parameter.numSimRuns):
                args=(nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop[runID],pedPaths,param,runID)
                
                argList.append(args)
                
            resList = pool.starmap(self.worker, argList)
            
            #generate flat set from shallow list of sets
            for runFinalSet in resList:
                self.resultSet |= runFinalSet
            
    def worker(self,nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop,pedPaths,param,runID):
        simRun = SimulationRun(nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop,pedPaths,param,runID)
        
        saveObject(simRun.simOutputSet, param.outputFolder + "/simOutputSet_runID-%d.pkl" % runID)
        
        return simRun.simOutputSet
    