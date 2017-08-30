import simpy
from pedestrianNetwork import PedestrianNetwork
from population import Population
from transitSystem import TransitSystem
from parameter import Parameter
from simulationOutput import SimulationOutput

class LearningInstance(object):

    def __init__(self,nodes,edges,stations,areas,interfaces,platforms,trainDictRaw,travPop,popMemory,param,runID,instanceID):
        
        #final instance flag
        if (instanceID >= Parameter.learningInstances):
            param.isFinalInstance = True
        else:
            param.isFinalInstance = False
          
        #last learning instance flag
        if (instanceID == Parameter.learningInstances - 1):
            lastLearningInstance = True
        else:
            lastLearningInstance = False
        
        #last final instance flag
        if (instanceID == Parameter.learningInstances + Parameter.finalInstances - 1):
            lastFinalInstance = True
        else:
            lastFinalInstance = False
        
        #all the following should go into an iteration/instance
        simEnv = simpy.Environment()
        pedNet = PedestrianNetwork(nodes,edges,stations,areas,interfaces,platforms,simEnv)
        transSys = TransitSystem(trainDictRaw,simEnv,pedNet, param)
        travPop = Population(travPop,pedNet,transSys,popMemory, param)
        
        
        travPop.addToSimulation(simEnv, pedNet, transSys, popMemory)
        transSys.addToSimulation(simEnv, pedNet)
        
        #reset number of required explorations
        numEpisodesToExplore = popMemory.resetExplorationSet()
        
        #run queueing network
        simEnv.run()
        
        #print missing interface specifications
        if Parameter.showWarnings:
            print(pedNet.interfaceDebugSet)
        
        #reset potentials for en-route path choice (required for post-processing and further instances)
        popMemory.resetAllPotentials()
        
        if Parameter.textOutput and param.isFinalInstance:
            instanceLog = "Run: %d, learningInstance: %d\n" % (runID,instanceID)
            instanceLog += "total relevant cost: %.2f (%d travelers)\n" % travPop.getTotTravDisutility()
            instanceLog += "number of episodes left to explore: %d\n\n" % numEpisodesToExplore
            instanceLog += travPop.generateLog()
            instanceLog += transSys.generateLog()
            
            instanceLog += popMemory.generatePathList()
                        
            fileNameLog = param.fileNameLog + ("run_%d_instance_%d.txt" % (runID,instanceID))
            
            with open(fileNameLog, 'w') as logFile:
                logFile.write(instanceLog)
        
        if (runID == 0 and instanceID == 0 and Parameter.verboseOutput):
            #fileNamePedList = Parameter.fileNamePathList + ".txt"
            fileNameGraph = Parameter.fileNameGraph + ".png"
            pedNet.generateGraph(fileNameGraph)
            #popMemory.generatePathList(fileNamePedList)
            
        if param.isFinalInstance:
            #generate simulation output
            self.simOutput = SimulationOutput(pedNet, transSys, travPop, param)
            
        if lastLearningInstance:
            print("Run %d learning completed after %d instances (number of episodes left to explore: %d)" % (runID+1,instanceID+1,numEpisodesToExplore))
            
        if lastFinalInstance:
            print("Run %d completed after %d instances" % (runID+1,instanceID+1))
        
            
        
            
            