import math
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib2tikz import save as tikz_save
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
from parameter import Parameter
from stationMapUtrBijlAsdZShl import StationMapUtrBijlAsdZShl


class PostProcessing(object):

    def __init__(self, simulationResultSet, param):
        
        #contains a set of simulationOutput objects
        self.simResults = simulationResultSet    

        self.param = param
        
        self.numSimOutput = Parameter.numSimRuns*Parameter.finalInstances
        
        self.outputPath = param.outputFolder + '/' + param.postProcessFolder
        
        if Parameter.savePlots:
            #generate time ticks for time plots
            self.generateTimeTicks()
            
            #preprocessing
            self.computeAverageAreaDensities()
            self.loadAreaAttributes()
            
            #generate plots
            self.plotStreamFlows()
            self.plotAreaDensities()
            self.plotStationPlatformOccupancy()
            self.plotUtilityDistribution()
               
            self.plotRidershipDistribution()
            self.plotFacilityLOSDistribution()
            self.plotStationLOSEvolution()
             
            #validation plots
            self.compareGateStreamFlows()
            self.compareEquippedLinkFlows()
            self.aggregatePlatformFlows()
            self.comparePlatformDensities()
              
            #heatmaps
            self.plotHeatmap()
        
    def generateTimeTicks(self):
        self.timeTickPos = [self.param.analysisStart + x*Parameter.analysisPlotInterval \
            for x in range( int( (self.param.analysisEnd-self.param.analysisStart)/Parameter.analysisPlotInterval ) + 1) ]
        self.timeTickLabel = list()
        
        for totalSec in self.timeTickPos:
            m, s = divmod(totalSec, 60)
            h, m = divmod(m, 60)
            assert(s==0), "xTickLabels should be chosen such that they do not contain seconds. (%s corresponds to %d:%02d:%02d)" % \
                (totalSec, h, m, s)
            self.timeTickLabel.append("%d:%02d" % (h, m) )
        
    def configureTimeAxis(self, ax):
        plt.xlim(self.param.analysisStart, self.param.analysisEnd)
        ax.set_xticks(self.timeTickPos)
        ax.set_xticklabels(self.timeTickLabel)
    
    def generateFigure(self, filename, fig, tikz=None):
        if tikz is None:
            drawTikz = Parameter.exportTIKZ
        else:
            assert(tikz == True or tikz == False)
            drawTikz = tikz
        
        if Parameter.savePlots: plt.savefig(filename + '.pdf', bbox_inches='tight') 
        if drawTikz: tikz_save(filename + '.tex', figure=fig, show_info=False)
        
    def plotStationLOSEvolution(self):
        
        #container of the form usersPerServiceLevel[stationName][serviceLevel][timeStep]
        usersPerServiceLevel = dict()
        
        #initialize
        for stationName in Parameter.stationNameDict.values():
            usersPerServiceLevel[stationName] = {serviceLevel:[0]*Parameter.numTimePointsAnalysis \
                for serviceLevel in Parameter.losLevels}
        
        for areaName in Parameter.plotStationLOSEvolutionAreas:
            stationName = self.areaStationNameDict[areaName]
            areaType = self.areaTypeDict[areaName]
            areaSize = self.areaSizeDict[areaName]
            
            for timeStep in range(0,Parameter.numTimePointsAnalysis):
                
                curDensity = self.avgAreaDensityDict[areaName][timeStep]
                curOccupation = curDensity*areaSize
                curServiceLevel = self.getLOS(areaType, curDensity)
                
                usersPerServiceLevel[stationName][curServiceLevel][timeStep] += curOccupation 
         
        for stationName in usersPerServiceLevel.keys():
            
            occupList = list()
            colorList = list()
            
            for serviceLevel in Parameter.losLevels:
                occupList.append( usersPerServiceLevel[stationName][serviceLevel] )
                colorList.append( Parameter.losLevelColors[serviceLevel] )
                
            figLOSDist = plt.figure()
            ax = figLOSDist.add_subplot(1, 1, 1)
            plt.stackplot(self.param.timePointsAnalysis, occupList, labels=Parameter.losLevels, colors=colorList)
                
            self.configureTimeAxis(ax)
            plt.ylabel('number of pedestrians')
            plt.title(stationName)
            
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[::-1], labels[::-1], title='LOS')
            
            filenameLOSDist = "%s/serviceDistr_%s" % (self.outputPath, stationName)
            self.generateFigure(filenameLOSDist, figLOSDist, tikz=False)
            
            #generate text output since figure cannot be exported as tikz
            filename = self.outputPath + '/serviceDistr_' + stationName
            
            #generate header of text output file
            servDistStr = "timePoints"
            
            for label in Parameter.losLevels:
                servDistStr += " %s" % label
            
            servDistStr += "\n"
            
            for timeIndex in range(0,len(self.param.timePointsAnalysis)):
                servDistStr += "%s " % self.param.timePointsAnalysis[timeIndex]
                
                for servLevelIndex in range(0,len(Parameter.losLevels)):
                    servDistStr += "%s " % occupList[servLevelIndex][timeIndex]
                    
                servDistStr += "\n"
                    
            with open(filename + ".txt", "w") as text_file:
                print(servDistStr, file=text_file)  
                        
        #close figure to reduce memory usage
        plt.close("all")    
    
    def plotFacilityLOSDistribution(self):
        
        assert( isinstance(Parameter.plotAreasLOSDistribution,list) ), "Type of Parameter.plotAreasLOSDistribution is %s, but should be 'list.'" % \
            type(Parameter.plotAreasLOSDistribution)
        
        losObsDict = dict() #histogram of observed LOS levels (infrastructure-oriented)
        losObsExpDict = dict() #histogram of experienced LOS levels (passenger-oriented)
        
        for areaName in Parameter.plotAreasLOSDistribution:
            
            areaType = self.areaTypeDict[areaName]
            densityList = self.avgAreaDensityDict[areaName]
            
            losObsDict[areaName] = {losLevel:0 for losLevel in Parameter.losLevels}
            losObsExpDict[areaName] = {losLevel:0 for losLevel in Parameter.losLevels}
            
            cumDensArea = sum(densityList)
            
            if cumDensArea == 0:
                print("Warning: Area %s has zero density during entire analysis period" % areaName)
                
            
            for curDens in densityList:
                curLOS = self.getLOS(areaType, curDens)
                
                losObsDict[areaName][curLOS] += 1/Parameter.numTimePointsAnalysis
                
                if cumDensArea > 0:
                    losObsExpDict[areaName][curLOS] += curDens/cumDensArea
                else:
                    assert(curDens == 0)
                    losObsExpDict[areaName][curLOS] += 0
        
        ### plot
        ind = range(0,len( Parameter.plotAreasLOSDistribution ))       # the x locations for areas of interest
        width = 0.35       # the width of the bars
        
        #initialize figure infrastructure-based LOS distribution
        figLOS, axLOS = plt.subplots()
        
        numObsLOS = [0]*len(Parameter.plotAreasLOSDistribution)
        numObsCumLOS = [0]*len(Parameter.plotAreasLOSDistribution)
        previousObsLOS = [0]*len(Parameter.plotAreasLOSDistribution)
        
        for serviceLevel in reversed(Parameter.losLevels):
            for areaIndex in range(0,len(Parameter.plotAreasLOSDistribution)):
                areaName = Parameter.plotAreasLOSDistribution[areaIndex]
                
                numObsLOS[areaIndex] = losObsDict[areaName][serviceLevel]
                numObsCumLOS[areaIndex] += previousObsLOS[areaIndex]
                previousObsLOS[areaIndex] = losObsDict[areaName][serviceLevel]
            
            axLOS.bar(ind, numObsLOS, width, label=serviceLevel, bottom=numObsCumLOS, color=Parameter.losLevelColors[serviceLevel])
        
        #set title and xticks
        axLOS.set_title('Infrastructure-oriented level-of-service')
        axLOS.set_xticks(ind)
        axLOS.set_xticklabels(Parameter.plotAreasLOSDistribution)
        
        #show legend entries in correct order
        handles, labels = axLOS.get_legend_handles_labels()
        axLOS.legend(handles[::-1], labels[::-1])
        
        #show y-axis in percent
        vals = axLOS.get_yticks()
        axLOS.set_yticklabels(['{:3.0f}%'.format(x*100) for x in vals])
        
        #save figure
        filenameLOS = self.outputPath + "/losInfrastructure"
        self.generateFigure(filenameLOS, figLOS)
        
        #initialize figure experienced LOS
        figExpLOS, axExpLOS = plt.subplots()
        
        numObsExpLOS = [0]*len(Parameter.plotAreasLOSDistribution)
        numObsCumExpLOS = [0]*len(Parameter.plotAreasLOSDistribution)
        previousObsExpLOS = [0]*len(Parameter.plotAreasLOSDistribution)
        
        for serviceLevel in reversed(Parameter.losLevels):
        
            for areaIndex in range(0,len(Parameter.plotAreasLOSDistribution)):
                areaName = Parameter.plotAreasLOSDistribution[areaIndex]
                
                numObsExpLOS[areaIndex] = losObsExpDict[areaName][serviceLevel]
                numObsCumExpLOS[areaIndex] += previousObsExpLOS[areaIndex]
                previousObsExpLOS[areaIndex] = losObsExpDict[areaName][serviceLevel]
            
            axExpLOS.bar(ind, numObsExpLOS, width, label=serviceLevel, bottom=numObsCumExpLOS, color=Parameter.losLevelColors[serviceLevel])
            
        #set title and xticks
        axExpLOS.set_title('Experienced level-of-service')
        axLOS.set_xticks(ind)
        axExpLOS.set_xticklabels(Parameter.plotAreasLOSDistribution)
        
        #show legend entries in correct order
        handles, labels = axExpLOS.get_legend_handles_labels()
        axExpLOS.legend(handles[::-1], labels[::-1])
        
        #show y-axis in percent
        vals = axExpLOS.get_yticks()
        axExpLOS.set_yticklabels(['{:3.0f}%'.format(x*100) for x in vals])
        
        #save figure
        filenameExpLOS = self.outputPath + '/losExperienced'
        self.generateFigure(filenameExpLOS, figExpLOS)

        #close figure to reduce memory usage
        plt.close("all")
        
        
#         #initialize figures
#         figLOS = plt.figure()
#         axLOS = figLOS.add_subplot()
#         
#         figExpLOS = plt.figure()
#         axExpLOS = figExpLOS.add_subplot()
#         
#         numObsLOS = [0]*len(Parameter.plotAreasLOSDistribution)
#         numObsCumLOS = [0]*len(Parameter.plotAreasLOSDistribution)
#         previousObsLOS = [0]*len(Parameter.plotAreasLOSDistribution)
#         
#         numObsExpLOS = [0]*len(Parameter.plotAreasLOSDistribution)
#         numObsCumExpLOS = [0]*len(Parameter.plotAreasLOSDistribution)
#         previousObsExpLOS = [0]*len(Parameter.plotAreasLOSDistribution)
#         
#         for serviceLevel in reversed(Parameter.losLevels):
# 
#             for areaIndex in range(0,len(Parameter.plotAreasLOSDistribution)):
#                 areaName = Parameter.plotAreasLOSDistribution[areaIndex]
#                 
#                 numObsLOS[areaIndex] = losObsDict[areaName][serviceLevel]
#                 numObsCumLOS[areaIndex] += previousObsLOS[areaIndex]
#                 previousObsLOS[areaIndex] = losObsDict[areaName][serviceLevel]
#                 
#                 numObsExpLOS[areaIndex] = losObsExpDict[areaName][serviceLevel]
#                 numObsCumExpLOS[areaIndex] += previousObsExpLOS[areaIndex]
#                 previousObsExpLOS[areaIndex] = losObsExpDict[areaName][serviceLevel]
#                             
#             axLOS.bar(ind, numObsLOS, width, label=serviceLevel, bottom=numObsCumLOS, color=Parameter.losLevelColors[serviceLevel])
#             axExpLOS.bar(ind, numObsExpLOS, width, label=serviceLevel, bottom=numObsCumExpLOS, color=Parameter.losLevelColors[serviceLevel])
#             
#         #set title and xticks
#         axLOS.set_title('Infrastructure-oriented level-of-service')
#         axLOS.set_xticks(ind)
#         axLOS.set_xticklabels(Parameter.plotAreasLOSDistribution)
#         
#         axExpLOS.set_title('Experienced level-of-service')
#         axLOS.set_xticks(ind)
#         axExpLOS.set_xticklabels(Parameter.plotAreasLOSDistribution)
#         
#         #show legend entries in correct order
#         handles, labels = axLOS.get_legend_handles_labels()
#         axLOS.legend(handles[::-1], labels[::-1])
#         
#         handles, labels = axExpLOS.get_legend_handles_labels()
#         axExpLOS.legend(handles[::-1], labels[::-1])
#         
#         #show y-axis in percent
#         vals = axLOS.get_yticks()
#         axLOS.set_yticklabels(['{:3.0f}%'.format(x*100) for x in vals])
#         
#         vals = axExpLOS.get_yticks()
#         axExpLOS.set_yticklabels(['{:3.0f}%'.format(x*100) for x in vals])
#         
#         #save figure
#         filenameLOS = 'output/losInfrastructure'
#         self.generateFigure(filenameLOS, figLOS)
#         
#         filenameExpLOS = 'output/losExperienced'
#         self.generateFigure(filenameExpLOS, figExpLOS)
            
    def loadAreaAttributes(self):
        stationMap = StationMapUtrBijlAsdZShl()
        areaSet = stationMap.areas
        
        self.areaTypeDict = dict()
        self.areaSizeDict = dict()
        self.areaStationNameDict = dict()
        
        for (areaName, areaSize, areaType, stationName) in areaSet:
            self.areaTypeDict[areaName] = areaType
            self.areaSizeDict[areaName] = areaSize
            self.areaStationNameDict[areaName] = stationName
        
        
    def computeAverageAreaDensities(self):
        
        #dict containing for each areaName the vector of average densities (corresponding to Parameter.numTiePointsAnalysis)
        self.avgAreaDensityDict = dict()
        
        #compute average densities of all areas
        for simOutput in self.simResults:
            
            for areaName, densityList in simOutput.areaDensityDict.items():
                
                #initialize average density list for each area
                if areaName not in self.avgAreaDensityDict.keys():
                    self.avgAreaDensityDict[areaName] = [0]*Parameter.numTimePointsAnalysis
                     
                #add weighted densities
                self.avgAreaDensityDict[areaName] = [x[0]+x[1]/self.numSimOutput for x in zip(self.avgAreaDensityDict[areaName],densityList)]
    
    def plotHeatmap(self):
        #import area coordinates and attributes
        areaCoords = pd.read_csv(Parameter.filenameAreaCoord)
        
        #initialize map
        figHeatMap = plt.subplots()
        
        #each area represents a polygon and has areaType and associated stationName
        polygonDict = dict()
        areaTypeDict = dict()
        areaStationNameDict = dict()
        
        xCoord = list()
        yCoord = list()

        stationAreaSets = dict()
        stationSet = set()
        
        #load each area
        for _, octagon in areaCoords.iterrows():
            #polygon = Polygon(np.random.rand(N,2), True)
            xCoord.clear()
            yCoord.clear()
            
            polygonName = octagon['areaName']
            polygonAreaType = octagon['areaType']
            polygonStationName = octagon['stationName']
            
            xCoord.append( octagon['x1'] )
            xCoord.append( octagon['x2'] )
            xCoord.append( octagon['x3'] )
            xCoord.append( octagon['x4'] )
            
            yCoord.append( octagon['y1'] )
            yCoord.append( octagon['y2'] )
            yCoord.append( octagon['y3'] )
            yCoord.append( octagon['y4'] )
            
            #add more polygon corners if needed
            if not math.isnan(octagon['x5']):
                xCoord.append( octagon['x5'] )
                yCoord.append( octagon['y5'] )
                
            if not math.isnan(octagon['x6']):
                xCoord.append( octagon['x6'] )
                yCoord.append( octagon['y6'] )
                
            if not math.isnan(octagon['x7']):
                xCoord.append( octagon['x7'] )
                yCoord.append( octagon['y7'] )
                
            if not math.isnan(octagon['x8']):
                xCoord.append( octagon['x8'] )
                yCoord.append( octagon['y8'] )                
            
            (xCoordCorr, yCoordCorr) = self.rotateMoveCoord(xCoord, yCoord, polygonStationName)
        
            coordMatrix = np.column_stack((xCoordCorr, yCoordCorr))
            
            #initialize all polygon with light-gray face and black edge
            polygon = Polygon(coordMatrix, edgecolor='k', facecolor='0.9', linewidth='0.1')
                
            polygonDict[polygonName] = polygon
            areaTypeDict[polygonName] = polygonAreaType
            areaStationNameDict[polygonName] = polygonStationName
            
            if polygonName in self.areaTypeDict.keys():
                assert(polygonAreaType == self.areaTypeDict[polygonName]), \
                    "Mismatch in area type for area %s: %s vs. %s" % (polygonName, self.areaTypeDict[polygonName], polygonAreaType)
            
            if polygonName in self.areaStationNameDict.keys():
                assert(polygonStationName == self.areaStationNameDict[polygonName]), \
                    "Mismatch in stationName for area %s: %s vs. %s" % (polygonName, self.areaStationNameDict[polygonName], polygonStationName)
            
            
            #add area to stationAreaSets
            if polygonStationName not in stationSet:
                stationSet.add(polygonStationName)
                stationAreaSets[polygonStationName] = set()
            
            if not polygonAreaType == "obstacle":
                stationAreaSets[polygonStationName].add(polygonName)
            
            plt.gca().add_patch(polygon)
        
        #draw contourlines
        for stationName, stationContour in Parameter.contourLines.items():
            #draw each line of contour
            for contourLine in stationContour:
                xList,yList = zip(*contourLine)
                
                xListCorr,yListCorr = self.rotateMoveCoord(xList, yList, stationName)
                
                plt.plot(xListCorr, yListCorr, color='k', linewidth=0.5)
        
        plt.axis('equal')
        plt.axis('off')
        
        #get maximum density over time over all areas to scale color map
        #maxAvgDens = max([max(areaDensList) for areaDensList in self.avgAreaDensityDict.values()])
        
        #generate density heat map
        for timeStep in range(0,Parameter.numTimePointsAnalysis):
            for stationName in stationSet:
                for areaName in stationAreaSets[stationName]:
                    polygon = polygonDict[areaName]
                    density = self.avgAreaDensityDict[areaName][timeStep]
                    
                    #relDens = density/maxAvgDens
                    #assert(density <= maxAvgDens)
                    relDens = min(1,density/Parameter.plotMaxDensity)
                    
                    #interpolate between white and blue to get color
                    polygon.set_facecolor([1-relDens, 1-relDens, 1])
            
            figTitle = "%s (maxDens: %.2f)" % (self.param.datePointsAnalysis[timeStep], Parameter.plotMaxDensity)
            plt.title(figTitle)
            
            filename = '%s/heatmaps/densityMap-%03d' % (self.outputPath, timeStep)
            self.generateFigure(filename, figHeatMap, tikz=False)
        
        #generate LOS map        
        for timeStep in range(0,Parameter.numTimePointsAnalysis):
            for stationName in stationSet:
                for areaName in stationAreaSets[stationName]:
                    
                    polygon = polygonDict[areaName]
                    areaType = areaTypeDict[areaName]
                    
                    density = self.avgAreaDensityDict[areaName][timeStep]
                    serviceLevel = self.getLOS(areaType,density)
                    serviceColor = Parameter.losLevelColors[serviceLevel]
                    
                    polygon.set_facecolor(serviceColor)
            
            figTitle = "Level-of-service, %s" % self.param.datePointsAnalysis[timeStep]
            plt.title(figTitle)
            
            filename = '%s/heatmaps/losMap-%03d' % (self.outputPath, timeStep)
            self.generateFigure(filename, figHeatMap, tikz=False)
        
        #generate average density and LOS map for peak period
        numTimeStepsPeak = int( Parameter.peakPeriodDuration // self.param.timeStepAnalysis )
        stationPeakPeriod = dict()
        peakDensityDict = dict()
        peakLOSDict = dict()
        maxPeakAvgDensity = 0
        
        #compute average peak conditions for each station
        for stationName in stationSet:
            occupList = self.platformOccupationDict[stationName]
            
            #determine peak period for each station
            maxPeriodOccup = 0
            periodStartStep = None
            
            for timeStep in range(0,Parameter.numTimePointsAnalysis-numTimeStepsPeak):
                periodOcc = sum(occupList[timeStep:timeStep+numTimeStepsPeak])
                
                if periodOcc > maxPeriodOccup:
                    periodStartStep = timeStep
                    maxPeriodOccup = periodOcc
            
            
            
            stationPeakPeriod[stationName] = "%s to %s" % (self.param.datePointsAnalysis[periodStartStep], \
                self.param.datePointsAnalysis[periodStartStep+numTimeStepsPeak])
            
            #compute average density and LOS during peak period
            for areaName in stationAreaSets[stationName]:
                densityList = self.avgAreaDensityDict[areaName]
                peakMeanDensity = sum(densityList[timeStep:timeStep+numTimeStepsPeak])/numTimeStepsPeak
                areaType = areaTypeDict[areaName]
                peakMeanLOS = self.getLOS(areaType, peakMeanDensity)
                
                peakDensityDict[areaName] = peakMeanDensity
                peakLOSDict[areaName] = peakMeanLOS
                
                if peakMeanDensity > maxPeakAvgDensity:
                    maxPeakAvgDensity = peakMeanDensity
             
        #draw peak-period density map (for all stations jointly)
        figTitle = "Average peak density (max density: %.2f)\n" % maxPeakAvgDensity
        for stationName in stationSet:
            figTitle += "%s: %s\n" % (stationName, stationPeakPeriod[stationName])
            
            for areaName in stationAreaSets[stationName]:
                polygon = polygonDict[areaName]
                density = peakDensityDict[areaName]
                
                relDens = density/maxPeakAvgDensity
                
                #interpolate between white and blue to get color
                polygon.set_facecolor([1-relDens, 1-relDens, 1])
                
                
        
        plt.title(figTitle)
        
        filename = self.outputPath + '/peakDensityMap'
        self.generateFigure(filename, figHeatMap, tikz=False)     
                
        #draw peak-period LOS map (for all stations jointly)
        figTitle = "Average peak level-of-service\n"
        for stationName in stationSet:
            figTitle += "%s: %s\n" % (stationName, stationPeakPeriod[stationName])
            
            for areaName in stationAreaSets[stationName]:
                polygon = polygonDict[areaName]
                serviceLevel = peakLOSDict[areaName]
                
                serviceColor = Parameter.losLevelColors[serviceLevel]
                
                polygon.set_facecolor(serviceColor)
        
        plt.title(figTitle)
        
        filename = self.outputPath + '/peakLOSMap'
        self.generateFigure(filename, figHeatMap, tikz=False) 
            
        #close figure to reduce memory usage
        plt.close("all")
        
    def plotRidershipDistribution(self):
        
        trainIDSet = set( next(iter(self.simResults)).totalRidershipLogDict.keys() )
                        
        for trainID in trainIDSet:
            #flag for non-corridor trains
            auxiliaryTrain = False
            
            ridershipTotal = dict()
            ridershipTracked = dict()
            ridershipAuxiliary = dict()
            
            numVehicles = None
            
            #compute average vehicle ridership            
            for simOutput in self.simResults:
                #initialize numVehicles if necessary
                if numVehicles is None:
                    numVehicles = len( simOutput.totalRidershipLogDict[trainID] )
                    
                if auxiliaryTrain:
                    break
                                                                        
                for stationName in Parameter.plotRidershipStations:
                    
                    if stationName not in simOutput.totalRidershipLogDict[trainID][0]:                        
                        auxiliaryTrain = True
                        break
                    
                    #initialize ridership lists
                    if stationName not in ridershipTotal.keys():
                        ridershipTotal[stationName] = [0]*numVehicles
                        ridershipTracked[stationName] = [0]*numVehicles
                        ridershipAuxiliary[stationName] = [0]*numVehicles
                        
                    for vehID in range(0,numVehicles):
                        #add weighted estimate of current simulation run    
                        ridershipTotal[stationName][vehID] += \
                            simOutput.totalRidershipLogDict[trainID][vehID][stationName]/self.numSimOutput
                        ridershipTracked[stationName][vehID] += \
                            simOutput.trackedRidershipLogDict[trainID][vehID][stationName]/self.numSimOutput
                        ridershipAuxiliary[stationName][vehID] += \
                            simOutput.auxiliaryRidershipLogDict[trainID][vehID][stationName]/self.numSimOutput
            
            #skip train if auxiliary
            if auxiliaryTrain:
                continue
            
            #generate plots                        
            for stationName in Parameter.plotRidershipStations:
                loadTrackedPass = ridershipTracked[stationName]
                loadAuxPass = ridershipAuxiliary[stationName]
               
                if numVehicles is None:
                    numVehicles = len( loadTrackedPass )
            
                ind = range(numVehicles,0,-1)       # the x locations for the train vehicles, arranging vehicles in direction of traveling (left to right)
                width = 0.9       # the width of the bars: can also be len(x) sequence
                
                curFig = plt.subplots()
                
                pAux = plt.bar(ind, loadAuxPass, width)
                pTrack = plt.bar(ind, loadTrackedPass, width, bottom=loadAuxPass)
                
                plt.xlabel('train vehicle')
                plt.ylabel('ridership')
                plt.title('Ridership by vehicle of train %s in %s (tot = %.1f)' % (trainID, stationName, sum(loadTrackedPass)+sum(loadAuxPass)) )
                plt.xticks(ind, range(1,numVehicles+1))
                plt.legend((pTrack[0], pAux[0]), ('corridor (N=%.1f)' % sum(loadTrackedPass), 'auxiliary (N=%.1f)' % sum(loadAuxPass) ))
                
                filename = '%s/ridershipDistribution_%s_%s' % (self.outputPath, trainID, stationName)
                
                with open(filename + ".txt", "w") as text_file:
                    print("loadTrackedPass: %s\n\nloadAuxPass: %s" % (loadTrackedPass, loadAuxPass), file=text_file)

                self.generateFigure(filename, curFig, tikz=False)
                
                plt.close()
        
        #close figure to reduce memory usage
        plt.close("all")    
            
    def plotUtilityDistribution(self):
        activityTypes = {'walking','waiting','riding'}
        
        avgUtilityDict = dict()
        stDevUtilityDict = dict()
        
        for connection in Parameter.plotConnections:
            
            #curMean = 
            avgUtilityDict[connection] = dict()
            
            #curStDev = 
            stDevUtilityDict[connection] = dict()
            
            for simOutput in self.simResults:
                            
                for activity in activityTypes:
                    #initialize if needed
                    if activity not in avgUtilityDict[connection]:
                        avgUtilityDict[connection][activity] = 0
                        stDevUtilityDict[connection][activity] = 0
                    
                    #add weighted estimate of current simulation run    
                    avgUtilityDict[connection][activity] += simOutput.avgConnUtility[connection][activity]/self.numSimOutput
                    stDevUtilityDict[connection][activity] += simOutput.stDevConnUtility[connection][activity]/self.numSimOutput
                    
        walkCostMean = list()
        waitCostMean = list()
        walkAndWaitCostMean = list()
        rideCostMean = list()
        
        walkCostStDev = list()
        waitCostStDev = list()
        rideCostStDev = list()
        
        connectionNames = list()
        
        for connection in Parameter.plotConnections:
            
            walkCostMean.append( -avgUtilityDict[connection]['walking'] )
            waitCostMean.append( -avgUtilityDict[connection]['waiting'] )
            walkAndWaitCostMean.append( -avgUtilityDict[connection]['walking'] - avgUtilityDict[connection]['waiting'] )
            rideCostMean.append( -avgUtilityDict[connection]['riding'] )
            
            walkCostStDev.append( stDevUtilityDict[connection]['walking'] )
            waitCostStDev.append( stDevUtilityDict[connection]['waiting'] )
            rideCostStDev.append( stDevUtilityDict[connection]['riding'] )
            
            connectionNames.append("%s -- %s" % (connection[0],connection[1]))
        
        ind = range(0,len( Parameter.plotConnections ))       # the x locations for the connections
        width = 0.35       # the width of the bars: can also be len(x) sequence
        
        figBar = plt.subplots()
        
        pWalk = plt.bar(ind, walkCostMean, width, yerr=walkCostStDev)
        pWait = plt.bar(ind, waitCostMean, width, bottom=walkCostMean, yerr=waitCostStDev)
        pRide = plt.bar(ind, rideCostMean, width, bottom=walkAndWaitCostMean, yerr=rideCostStDev)
        
        plt.ylabel('cost [EUR]')
        plt.title('Travel cost by OD-relation and travel activity')
        plt.xticks(ind, connectionNames)
        plt.legend((pRide[0], pWait[0], pWalk[0]), ('Riding', 'Waiting', 'Walking'))
        
        #plt.show()
        filename = self.outputPath + '/travelDisutilityStackedBar'

        with open(filename + ".txt", "w") as text_file:
            print("avgUtilityDict: %s\n\nstDevUtilityDict: %s" % (avgUtilityDict, stDevUtilityDict), file=text_file)
        
        self.generateFigure(filename, figBar, tikz=False)
        
        
        #close figure to reduce memory usage
        plt.close("all")
        
    def plotStationPlatformOccupancy(self):
        
        self.platformOccupationDict = dict()
        
        for stationName in Parameter.plotStations:
            #sum occupation over all simulation runs
            totOccupupation = [0]*Parameter.numTimePointsAnalysis
            for simOutput in self.simResults:
                totOccupupation = [sum(x) for x in zip(totOccupupation, simOutput.stationPlatformOccupationDict[stationName])]
                
            #compute mean simulation over simulations
            occupPoints = [totOcc/self.numSimOutput for totOcc in totOccupupation]
            
            #store platform occupation
            self.platformOccupationDict[stationName] = occupPoints

            curFig, ax = plt.subplots()
    
            plt.plot(self.param.timePointsAnalysis,occupPoints)
            plt.ylabel('Number of pedestrians')
            plt.title("Occupation on platform area in %s" % stationName)
            self.configureTimeAxis(ax)
            
            filename = '%s/platformOccupation_%s' % (self.outputPath, stationName)
            self.generateFigure(filename, curFig)
        
        #close figure to reduce memory usage
        plt.close("all")
    
    
    def compareEquippedLinkFlows(self):
        
        #load flow observations
        timeName = {'Time': 'timeStamp'}

        asdzSens = {'asdz-PF2_escalator In': 'asdzEscIn', 'asdz-PF2_escalator Out': 'asdzEscOut', 'asdz-PF2_stairs In': 'asdzStairsIn', 'asdz-PF2_stairs Out': 'asdzStairsOut'}
        
        utSens = {'ut-Esc_north In': 'utEscNorthIn', 'ut-Esc_north Out': 'utEscNorthOut', 'ut-Esc_south In': 'utEscSouthIn', 'ut-Esc_south Out': 'utEscSouthOut', 'ut-Stairs_north In': 'utStairsNorthIn', 'ut-Stairs_south In': 'utStairsSouthIn', 'ut-Stairs_north Out': 'utStairsNorthOut', 'ut-Stairs_south Out': 'utStairsSouthOut'}
        
        shlSens = {'Perron 2 hellingbaan Noord (AMS_SCHI11) In': 'shlRampNorthIn', 'Perron 2 hellingbaan Noord (AMS_SCHI11) Out': 'shlRampNorthOut', 'Perron 2 roltrap Noord (AMS_SCHI10) In': 'shlEscNorthIn', 'Perron 2 roltrap Noord (AMS_SCHI10) Out': 'shlEscNorthOut', 'Perron 2 roltrap Zuid (AMS_SCHI12) In': 'shlEscStairsSouthIn', 'Perron 2 roltrap Zuid (AMS_SCHI12) Out': 'shlEscStairsSouthOut', 'Perron 2 hellingbaan Zuid (AMS_SCHI9) In': 'shlRampSouthIn', 'Perron 2 hellingbaan Zuid (AMS_SCHI9) Out': 'shlRampSouthOut'}
        
        dateparse = lambda x: pd.datetime.strptime(x, '%d.%m.%y %H:%M')
        
        asdzLinkFlowDat = pd.read_csv(Parameter.asdzLinkFlowObsFile, sep=';',
            usecols = set(asdzSens.keys()) | set(timeName.keys()), parse_dates=["Time"], date_parser=dateparse)
        asdzLinkFlowDat.rename(columns={**timeName,**asdzSens}, inplace=True)
        
        utLinkFlowDat = pd.read_csv(Parameter.utLinkFlowObsFile, sep=';',
            usecols = set(utSens.keys()) | set(timeName.keys()), parse_dates=["Time"], date_parser=dateparse)
        utLinkFlowDat.rename(columns={**timeName,**utSens}, inplace=True)
        
        shlLinkFlowDat = pd.read_csv(Parameter.shlLinkFlowObsFile, sep=';',
            usecols = set(shlSens.keys()) | set(timeName.keys()), parse_dates=["Time"], date_parser=dateparse)
        shlLinkFlowDat.rename(columns={**timeName,**shlSens}, inplace=True)
        
        
        #prepare filtered and sorted observations (sorting in principle not required)
        asdzObsSorted = asdzLinkFlowDat.loc[(self.param.dateAnalysisStart <= asdzLinkFlowDat['timeStamp']) & (asdzLinkFlowDat['timeStamp'] <= self.param.dateAnalysisEnd)].sort_values(by='timeStamp')
        asdzTimeList = [date.total_seconds() for date in (asdzObsSorted['timeStamp']-self.param.midnightCaseStudy).tolist()]
        
        utObsSorted = utLinkFlowDat.loc[(self.param.dateAnalysisStart <= utLinkFlowDat['timeStamp']) & (utLinkFlowDat['timeStamp'] <= self.param.dateAnalysisEnd)].sort_values(by='timeStamp')
        utTimeList = [date.total_seconds() for date in (utObsSorted['timeStamp']-self.param.midnightCaseStudy).tolist()]
        
        shlObsSorted = shlLinkFlowDat.loc[(self.param.dateAnalysisStart <= shlLinkFlowDat['timeStamp']) & (shlLinkFlowDat['timeStamp'] <= self.param.dateAnalysisEnd)].sort_values(by='timeStamp')
        shlTimeList = [date.total_seconds() for date in (shlObsSorted['timeStamp']-self.param.midnightCaseStudy).tolist()]
        
        self.ASEFlowCounts = dict()
        self.ASECumCounts = dict()
        self.ASETimePoints = dict()

        for linkName in asdzSens.values():
            self.ASEFlowCounts[linkName] = asdzObsSorted[linkName].tolist()
            self.ASECumCounts[linkName] = np.cumsum( asdzObsSorted[linkName].tolist() )
            self.ASETimePoints[linkName] = asdzTimeList

        for linkName in utSens.values():
            self.ASEFlowCounts[linkName] = utObsSorted[linkName].tolist()
            self.ASECumCounts[linkName] = np.cumsum( utObsSorted[linkName].tolist() )
            self.ASETimePoints[linkName] = utTimeList

        for linkName in shlSens.values():
            self.ASEFlowCounts[linkName] = shlObsSorted[linkName].tolist()
            self.ASECumCounts[linkName] = np.cumsum( shlObsSorted[linkName].tolist() )
            self.ASETimePoints[linkName] = shlTimeList
        
        #check consisteny of data: 
        assert( len(set(Parameter.flowSensorLinkNameDict.keys()) ^  set(self.ASECumCounts.keys())) == 0 ), \
            "Inconsistency between flowSensorLinkNameDict (%s) and self.ASECumCounts (%s)" % \
            (Parameter.flowSensorLinkNameDict.keys(), self.ASECumCounts.keys())
        
        #plot comparison
        for sensorName, linkName in Parameter.flowSensorLinkNameDict.items():
            #observation
            timeASE = self.ASETimePoints[sensorName]
            cumASE = self.ASECumCounts[sensorName]
            flowRateASE = self.ASEFlowCounts[sensorName]
            
            #simulation
            totCumSim = [0]*Parameter.numTimePointsAnalysis
            totflowRateSim = [0]*Parameter.numTimePointsAnalysis 
            
            for simOutput in self.simResults:
                totCumSim = [sum(x) for x in zip(totCumSim, simOutput.linkCumFlowDict[linkName])]
                totflowRateSim = [sum(x) for x in zip(totflowRateSim, simOutput.linkFlowRateDict[linkName])]
            
            cumSim = [totCum/self.numSimOutput for totCum in totCumSim]
            flowRateSim = [flowRate/self.numSimOutput for flowRate in totflowRateSim]
            
            #plotting cumulative flow
            figCum, axCum = plt.subplots()
            
            plt.ylabel('cumulative flow')
            plt.title(sensorName)
            
            plt.step(timeASE, cumASE, where='post', label='obs', color='blue')
            plt.step(self.param.timePointsAnalysis,cumSim, where='post',label='est', linestyle='dashed', color='blue')
        
            self.configureTimeAxis(axCum)
            plt.legend()
            
            filenameCum = '%s/sensor_%s_cumFlow' % (self.outputPath, sensorName)
            self.generateFigure(filenameCum, figCum)
            
            plt.close()
            
            #plotting flow rate
            figFlowRate, axFlowRate = plt.subplots()
            
            plt.ylabel('flow rate (ped/min)')
            plt.title(sensorName)
            
            plt.step(timeASE, flowRateASE, where='post', label='obs', color='blue')
            plt.step(self.param.timePointsAnalysis,flowRateSim, where='post',label='est', linestyle='dashed', color='blue')
        
            self.configureTimeAxis(axFlowRate)
            plt.legend()
            
            filenameFlowRate = '%s/sensor_%s_flowRate' % (self.outputPath, sensorName)
            self.generateFigure(filenameFlowRate, figFlowRate)
            
            plt.close()
            
    def aggregatePlatformFlows(self):
                
        for hyperStreamName, sensorNameSet in Parameter.aggregatedFlowValidation.items():
            
            #we assume that sensors within same hyperstream have the same time discretization
            randomSensorName = random.sample(sensorNameSet,1)[0]
            hyperStreamTimeObs = self.ASETimePoints[randomSensorName]
            
            hyperStreamCumObs = [0]*len(hyperStreamTimeObs)
            hyperStreamCumSim = [0]*Parameter.numTimePointsAnalysis
            
            for sensorName in sensorNameSet:
                hyperStreamCumObs = [sum(x) for x in zip(hyperStreamCumObs, self.ASECumCounts[sensorName] ) ]
                
                linkName = Parameter.flowSensorLinkNameDict[sensorName]
                for simOutput in self.simResults:
                    hyperStreamCumSim = [sum(x) for x in zip(hyperStreamCumSim, simOutput.linkCumFlowDict[linkName])]
                                
            #average over multiple simulation runs
            hyperStreamCumSim = [totCum/self.numSimOutput for totCum in hyperStreamCumSim]
            
            #plotting cumulative flow
            figCum, axCum = plt.subplots()
            
            plt.ylabel('cumulative flow')
            plt.title(hyperStreamName)
            
            plt.step(hyperStreamTimeObs, hyperStreamCumObs, where='post', label='ASE', color='blue')
            plt.step(self.param.timePointsAnalysis,hyperStreamCumSim, where='post',label='est', linestyle='dashed', color='blue')
        
            self.configureTimeAxis(axCum)
            plt.legend()
            
            filenameCum = '%s/hyperFlow_%s' % (self.outputPath, hyperStreamName)
            self.generateFigure(filenameCum, figCum)
            plt.close()
        
 
    
    def compareGateStreamFlows(self):
        
        relCol = ['Gebied', 'treinnummer', 'in_of_uit', 'gem_MsgReportDate', 'aantal_reizigers']
        dataTypes = {'Gebied':str, 'treinnummer':int, 'in_of_uit':str, 'gem_MsgReportDate':str, 'aantal_reizigers':float}
        colNames = ['gateID', 'trainNumber', 'inOut', 'timeStamp', 'count']
        
        trainIDStationSet = next(iter(self.simResults)).servedStationSet
        
        gateIDSetRockt = set()
        
        self.rocktGateCountIn = dict()
        self.rocktGateTimeIn = dict()
        self.rocktGateCountOut = dict()
        self.rocktGateTimeOut = dict()
        
        for inOutFile in Parameter.inUitFiles:
        
            gateLogs = pd.read_csv(inOutFile, usecols = relCol,dtype=dataTypes,parse_dates=["gem_MsgReportDate"])
    
            gateLogs.columns = colNames
            
            for logEntry in gateLogs.sort_values(by='timeStamp').values:
                
                gateID = logEntry[0]
                trainNumber = logEntry[1] 
                inOut = logEntry[2]
                timeStamp = logEntry[3]
                count = logEntry[4]
                
                #filter out logs outside of time window
                if not (self.param.dateAnalysisStart<timeStamp and timeStamp<self.param.dateAnalysisEnd):
                    continue
                
                #correct corrupted gateIDs
                if not (gateID in Parameter.rocktGateIDSetIn or gateID in Parameter.rocktGateIDSetOut):
                    
                    if gateID in Parameter.rocktGateIDCorrectionDict.keys():
                        gateID = Parameter.rocktGateIDCorrectionDict[gateID]
                    elif gateID in Parameter.utrechtCorruptedGateIDs:
                        #skip entries associated with corrupted gates
                        continue  
                    else:
                        print("Could not recover gateID %s. Skipping." % gateID)
                        
                #filter out logs associated with untracked trains
                if not (trainNumber in trainIDStationSet):
                    continue
                                
                stationName = Parameter.gateIDStationNameDict[gateID]
                if not (stationName in trainIDStationSet[trainNumber]):
                    #print("train %d exists, but does not serve %s. Affects %.2f pass." %\
                    #      (trainNumber, stationName,count))
                    
                    continue
                
                
                if not gateID in gateIDSetRockt:
                    gateIDSetRockt.add(gateID)
                    
                    self.rocktGateCountIn[gateID] = list()
                    self.rocktGateTimeIn[gateID] = list()
                    
                    self.rocktGateCountOut[gateID] = list()
                    self.rocktGateTimeOut[gateID] = list()
                    
                assert(inOut in {'I','U'})
                
                obsTime = (timeStamp - self.param.midnightCaseStudy).total_seconds()
                
                if inOut == 'I':
                    curCountLog = self.rocktGateCountIn[gateID]
                    curTimeLog = self.rocktGateTimeIn[gateID]
                elif inOut == 'U':
                    curCountLog = self.rocktGateCountOut[gateID]
                    curTimeLog = self.rocktGateTimeOut[gateID]
                    
                if len(curCountLog) == 0:
                    curCountLog.append(count)
                else:
                    curCountLog.append(curCountLog[-1] + count)
                        
                curTimeLog.append(obsTime)
        
        for gateID, inLinkName in Parameter.gateIDLinkNameDict.items():
            
            #assert(gateID in gateIDSetRockt), "gate %s not in %s" % (str(gateID), gateIDSetRockt)
            
            outLinkName = inLinkName[::-1]
            
            #simulation
            totCumIn = [0]*Parameter.numTimePointsAnalysis
            totCumOut = [0]*Parameter.numTimePointsAnalysis 
            
            for simOutput in self.simResults:
                totCumIn = [sum(x) for x in zip(totCumIn, simOutput.linkCumFlowDict[inLinkName])]
                totCumOut = [sum(x) for x in zip(totCumOut, simOutput.linkCumFlowDict[outLinkName])]
            
            cumInSim = [totCum/self.numSimOutput for totCum in totCumIn]
            cumOutSim = [totCum/self.numSimOutput for totCum in totCumOut]

            #plotting cumulative flow
            figCum, axCum = plt.subplots()
            
            #simulated data
            plt.step(self.param.timePointsAnalysis,cumInSim, where='post',label='est check-in', linestyle='dashed', color='red')
            plt.step(self.param.timePointsAnalysis,cumOutSim, where='post',label='est check-out', linestyle='dashed', color='blue')
                        
            #rockt data
            if gateID in gateIDSetRockt:
                plt.step(self.rocktGateTimeIn[gateID],self.rocktGateCountIn[gateID], where='post',label='obs check-in', color='red')
                plt.step(self.rocktGateTimeOut[gateID],self.rocktGateCountOut[gateID], where='post',label='obs check-out', color='blue')
            
            plt.ylabel('cumulative flow')
            plt.title(gateID)
            self.configureTimeAxis(axCum)
            plt.legend()
            filenameCum = '%s/gateFlow_%s' % (self.outputPath, gateID)
            self.generateFigure(filenameCum, figCum, tikz = False)
            plt.close()
        
        #close figure to reduce memory usage
        plt.close("all")
    
    def plotStreamFlows(self):
        
        for curStreamName in Parameter.plotLinkFlows:
            #accumulate curve flows from all simulations
            #totFlowRate = [0]*Parameter.numTimePointsAnalysis
            totCumFlow = [0]*Parameter.numTimePointsAnalysis
            
            for simOutput in self.simResults:                
                #totFlowRate = [sum(x) for x in zip(totFlowRate, simOutput.linkFlowRateDict[curStreamName])]
                
                totCumFlow = [sum(x) for x in zip(totCumFlow, simOutput.linkCumFlowDict[curStreamName])]            
            
            #flowRatePoints = [totRate/self.numSimOutput for totRate in totFlowRate]
            cumFlowPoints = [totCum/self.numSimOutput for totCum in totCumFlow]
                        
            #FLOW RATES are dangerous, as they depend on the time discretization. better stay with CDF
            #the below code produces mathematically correct, but potentially misleading results
            #to reduce intuitively accessible results, the unit of the flow rate (currently ped/min)
            #and the time discretization (currently 18s or so) should coincide
            #plotting flow rate
            #figRate, axRate = plt.subplots()
            #plt.plot(self.param.timePointsAnalysis,flowRatePoints)
            #plt.ylabel('inflow rate')
            #plt.title(curStreamName)
            #self.configureTimeAxis(axRate)
            #filenameRate = 'output/flowRate_%s-%s' % (curStreamName[0],curStreamName[1])
            #self.generateFigure(filenameRate, figRate)
            
            #plotting cumulative flow
            figCum, axCum = plt.subplots()
            plt.step(self.param.timePointsAnalysis,cumFlowPoints, where='post')
            plt.ylabel('cumulative inflow')
            plt.title(curStreamName)
            self.configureTimeAxis(axCum)
            filenameCum = '%s/cumFlow_%s-%s' % (self.outputPath, curStreamName[0],curStreamName[1])
            self.generateFigure(filenameCum, figCum)
        
        #close figure to reduce memory usage
        plt.close("all")
        
    def comparePlatformDensities(self):
        
        setSensorFloorField = set()
        dictSensorAreaID = dict()
        dictSensorSurfaceSize = dict()
        
        dictModelAreaSize = dict()
        
        linkFlowDat = pd.read_csv(Parameter.utFloorFieldLayoutFile)
        
        for sensorEntry in linkFlowDat.values:
            sensorName = sensorEntry[0]+sensorEntry[1]+str(sensorEntry[2])+sensorEntry[3]
            
            sensorSurfaceSize = sensorEntry[4]
            areaID = sensorEntry[5]
            areaSize = sensorEntry[6]
            
            setSensorFloorField.add(sensorName)
            dictSensorAreaID[sensorName] = areaID
            dictSensorSurfaceSize[sensorName] = sensorSurfaceSize
            dictModelAreaSize[areaID] = areaSize
        
        areaCoveredSurfaceDict = dict()
        areaObservationDict = dict()
        
        for sensorName in setSensorFloorField:
            
            areaID = dictSensorAreaID[sensorName]
            surfaceSize = dictSensorSurfaceSize[sensorName]
            
            if not areaID in areaCoveredSurfaceDict:
                areaCoveredSurfaceDict[areaID] = 0
                areaObservationDict[areaID] = dict()
                
            areaCoveredSurfaceDict[areaID] += surfaceSize
            
        
        occDat = pd.read_csv(Parameter.utFloorFieldOccupancyFile,\
            usecols=['eventtimestamp', 'counts', 'detectorobjectname'],\
            parse_dates=["eventtimestamp"])
                
        occDat.columns = ['timeStamp', 'accumulation', 'sensorName']
        
        for occObst in occDat.values:
            dateTimeStamp = pd.to_datetime(occObst[0])
            acc = occObst[1]
            sensor = occObst[2]
            
            #only consider relevant sensors
            if sensor not in setSensorFloorField:
                continue
            
            #only consider relevant times
            if not (self.param.dateAnalysisStart < dateTimeStamp and dateTimeStamp < self.param.dateAnalysisEnd):
                continue
            
            areaID = dictSensorAreaID[sensor]
            
            areaAccObsDict = areaObservationDict[areaID]
            
            if dateTimeStamp not in areaAccObsDict:
                areaAccObsDict[dateTimeStamp] = 0
                
            areaAccObsDict[dateTimeStamp] += acc
        
        for areaName, areaObs in areaObservationDict.items():
            
            secDensObs = list()
            areaSurfaceSizeObs = areaCoveredSurfaceDict[areaName]
            
            for dateTime, acc in areaObs.items():
                curSec = (dateTime-self.param.midnightCaseStudy).total_seconds()
                secDensObs.append( (curSec,acc/areaSurfaceSizeObs) )
           
            #sort list of tuples
            secDensObs.sort(key=lambda tup: tup[0])
            timeListObs, densListObs = zip(*secDensObs)
            
            #retrieve simulation data
            totDensSim = [0] * Parameter.numTimePointsAnalysis
            for simOutput in self.simResults:                
                totDensSim = [sum(x) for x in zip(totDensSim, simOutput.areaDensityDict[areaName])]
            
            densityPointsSim = [totDens/self.numSimOutput for totDens in totDensSim]
            
            
            curFig, ax = plt.subplots()
            plt.plot( timeListObs, densListObs, label="obs (%.1f m2)" % areaCoveredSurfaceDict[areaName], color='blue')
            plt.plot(self.param.timePointsAnalysis,densityPointsSim, label="est (%.1f m2)" % dictModelAreaSize[areaName], color='blue', linestyle='dashed')
            plt.ylabel('density')
            plt.ylim(0, Parameter.plotMaxDensity)
            plt.title(areaName)
            self.configureTimeAxis(ax)
            plt.legend()
            filename = '%s/platformDens_%s' % (self.outputPath, areaName)
            self.generateFigure(filename, curFig)
            
            plt.close()
            
            
    def plotAreaDensities(self):
        
        for curAreaName in Parameter.plotAreaDensities:
            #average area densities over all simulations
            totDensity = [0] * Parameter.numTimePointsAnalysis
            for simOutput in self.simResults:                
                totDensity = [sum(x) for x in zip(totDensity, simOutput.areaDensityDict[curAreaName])]
            
            densityPoints = [totDens/self.numSimOutput for totDens in totDensity]
                    
            curFig, ax = plt.subplots()
    
            plt.plot(self.param.timePointsAnalysis,densityPoints)
            plt.ylabel('density')
            plt.ylim(0, Parameter.plotMaxDensity)
            plt.title(curAreaName)
            self.configureTimeAxis(ax)
            
            filename = '%s/areaDensity_%s' % (self.outputPath, curAreaName)
            self.generateFigure(filename, curFig)
        
        #close figure to reduce memory usage
        plt.close("all")    

    def rotateMoveCoord(self, xList, yList, stationName):
    
        angle = Parameter.platformAngleDict[stationName]
        
        #rotate around origin
        ox, oy = Parameter.platformCoordinateCenterDict[stationName]
        
        xListCorr = list()
        yListCorr = list()
        
        for (px,py) in zip(xList,yList):
            qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy) + Parameter.platformTranslationDict[stationName][0]
            qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy) + Parameter.platformTranslationDict[stationName][1]
            
            xListCorr.append(qx)
            yListCorr.append(qy)
            
        return xListCorr, yListCorr
    
    def getLOS(self, areaType, density):
        
        #platform areas
        if areaType == "horizontal":
            losScale = Parameter.losWaitingFruin
        elif areaType == "escalator" or areaType == "stairway":
            losScale = Parameter.losStairsFruin
        else:
            print("Warning: Unknown area type: %s" % areaType)
        
        for index,losThreshold in enumerate(losScale):
            if density <= losThreshold:
                losLevel = Parameter.losLevels[index]
                break
        
        return losLevel
        