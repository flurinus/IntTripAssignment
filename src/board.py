import time
from methodLibrary import loadObject
from stationMapUtrBijlAsdZShl import StationMapUtrBijlAsdZShl
from rocktData import RocktData
from simulation import Simulation
from trentoData import TrentoData
from postProcessing import PostProcessing
import os


class Board(object):

    def __init__(self, param):
        
        print("case study date: %s" % param.dayCaseStudyString)
        
        if param.postProcessOnly and not param.postProcess:
            print("Set postProcess to True or postProcessOnly to False")
        
        elif param.postProcessOnly:
            path = param.outputFolder + '/'
            files = []
            for i in os.listdir(path):
                if os.path.isfile(os.path.join(path,i)) and 'simOutputSet' in i:
                    files.append(path + i)
            
            simResultSet = set()
            
            print("Loading pre-computed simulation runs (%d in total): " % len(files), end='', flush=True)    
            for file in files:
                print("%s, " % file[-11:-1], end='', flush=True)
                simResultSet |= loadObject(file)
            print("done.")
            
                
        else:
            #corridor Utrecht - Bijlmer - AsdZ - Schiphol
            mapUtBiAZ = StationMapUtrBijlAsdZShl() #read map data
            trentoUtBiAZ = TrentoData(param) #read train information
            rocktUtBiAZ = RocktData(param, trentoUtBiAZ) #read smart card information
        
            trainListFile = open(param.outputFolder + "/trainList.txt", 'w')
            trainListFile.write(str(trentoUtBiAZ))
            trainListFile.close()
            print("Data loaded.")
            
              
            start = time.time()
            simulation = Simulation(mapUtBiAZ.nodes, mapUtBiAZ.edges, mapUtBiAZ.stationNames, mapUtBiAZ.areas, mapUtBiAZ.interfaces, mapUtBiAZ.platformAttributes,
                       trentoUtBiAZ.getTrainDict(), rocktUtBiAZ, mapUtBiAZ.pedPaths, param)
              
            end = time.time()
            print('simulation time ' + str(end-start) +'s')
            
            simResultSet = simulation.resultSet
        
        if param.postProcess:
            print("Starting post-processing.")
            PostProcessing(simResultSet, param)
            print("post-processing done")
        else:
            print("Postprocessing deactivated.")
        
        