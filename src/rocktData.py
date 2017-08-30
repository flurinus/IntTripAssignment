import pandas as pd
from datetime import datetime
from random import random
from parameter import Parameter
from rocktTrain import RocktTrain
from rocktTraveler import RocktTraveler
from methodLibrary import weightedChoice

# import numpy as np
# import matplotlib.pyplot as plt

class RocktData(object):
    '''
    Reads and stores passenger information from NS' ROCKT database
    '''
    
    def __init__(self, param, trentoTrains):
        
        self.trentoTrains = trentoTrains
        
        #retrieve start and end date
        self.midnightCaseStudy = param.midnightCaseStudy #used as time origin to prevent negative times
        self.dayCaseStudyString = param.dayCaseStudyString
        
        #stores all train-related information of Automatic Fare Collection data (ROCKT, Overstapper, Ridership)
        self.trainDict = dict()
        
        #stores synthesized travelers
        self.travelerSet = set()

        #import augmented smart card logs (in- en uitstappers) 
        self.importInUitstapper(self.trentoTrains)
        
        #import transfers
        self.importOverstapper(self.trentoTrains)
        
        #import ridership for trains (needed for calculation of OD trips)
        self.importRidership(self.trentoTrains)
        
        #compute OD ratios from imported data for each train
        self.computeODRatios()
        
    def __repr__(self):
        rockDataStr = "\nSynthesized traveler population\n"
        
        for traveler in self.travelerSet:
            rockDataStr += "%s\n" % traveler
            
        rockDataStr += "(total: %d travelers)\n" % len(self.travelerSet)
        
        return rockDataStr

    #provide traveler database in format readable for pedQN
    def synthesizeTravelPopulation(self):
        #clear traveler dict
        self.travelerSet.clear()
        
        #synthesize travelers with one train leg
        self.synthesizeOneLegTravelers(self.trentoTrains)
        
        #synthesize transferring passengers
        self.synthesizeTwoLegTravelers(self.trentoTrains)
        
        #check of self-consistency
        #only required for validation
#         self.checkConsisteny(self.trentoTrains)
         
        travID = 0
        travPrefix = "Trav"
         
        travelerDict = dict()
         
        for curTraveler in self.travelerSet:
             
            travName = "%s%05i" % (travPrefix, travID)
            travID += 1
             
            travelerDict[travName] = curTraveler
         
        return travelerDict
    
    def loadInUitData(self, inUitFilePath, trentoTrains):
        
        relevantColumnsInUit = ['stationID', 'Gebied', 'treinnummer', 'av_verkeersdatum', 'Spoor_Real', 'in_of_uit', 'gem_MsgReportDate', 'aantal_reizigers']
        titleColumnsInUit = ['stationID', 'gateNode', 'trainNumber', 'date', 'trackNumber', 'InOut', 'gateTimeStamp', 'numTravelers']
        dataTypes = {'stationID':int, 'Gebied':str, 'treinnummer':int, 'av_verkeersdatum':str, 'Spoor_Real':str,
                     'in_of_uit':str, 'gem_MsgReportDate':str, 'aantal_reizigers':float}
        #read current incoming/outgoing passenger file and rename headers
        inUitRaw = pd.read_csv(inUitFilePath, usecols=relevantColumnsInUit, dtype=dataTypes)
        
        inUitRaw.columns = titleColumnsInUit
        
        #filter data based on date and train numbers
        inUitRawDataFiltered = inUitRaw.loc[ (inUitRaw['date'] == self.dayCaseStudyString) &\
            inUitRaw['trainNumber'].isin(trentoTrains.relevantTrainSet) ]
        
        return inUitRawDataFiltered
        
    ## Import ROCKT
    def importInUitstapper(self, trentoTrains):
        
        for inUitFilePath in Parameter.inUitFiles:
            
            inUitRawDataFiltered = self.loadInUitData(inUitFilePath, trentoTrains)
            
            for _, inUitEntry in inUitRawDataFiltered.iterrows():
                
                stationID = inUitEntry["stationID"]
                stationName = Parameter.stationNameDict[stationID]
                trainNumber = inUitEntry["trainNumber"]
                
                #check if train is served by modeled platform, otherwise skip
                if stationName not in trentoTrains.trainDict[trainNumber].stationNameSequence:
                    #skip current in/uit entry
                    continue
                
                gateNode = inUitEntry["gateNode"]
                inOut = inUitEntry["InOut"]
                numTravelers = inUitEntry["numTravelers"]
                gateTimeStampRaw = datetime.strptime( inUitEntry["gateTimeStamp"] , '%Y-%m-%dT%H:%M:%S' )
                gateTime = (gateTimeStampRaw - self.midnightCaseStudy).total_seconds()
                
                assert(gateTime >= 0), "Negative gate time (%.2f)" % gateTime
                    
                if trainNumber in self.trainDict.keys():
                    curTrain = self.trainDict[trainNumber]
                else:
                    curTrain = RocktTrain()
                    self.trainDict[trainNumber] = curTrain
                    
                assert(inOut == "U" or inOut == "I")
                
                if inOut == "U":
                    #add alighting volume
                    curTrain.addAlightIncoming(stationName, numTravelers)
                    
                    #add exit gate to store gate usage distribution
                    curTrain.addExitGateUsage(stationName, gateNode, gateTime, numTravelers)
                    
                elif inOut == "I":
                    curTrain.addBoardOutgoing(stationName, numTravelers)
                    
                    #add entrance gate to store gate usage distribution
                    curTrain.addEntranceGateUsage(stationName, gateNode, gateTime, numTravelers)
                    
                    
    def loadOverstapperData(self, overstapperFilePath, trentoTrains):
        
        relevantColumnsOverstapper = ['StationID', 'aankomst_verkeersdatum', 'aankomst_treinnummer', 'aankomst_moment', 'aankomst_spoor_real', \
                                      'vertrek_treinnummer', 'vertrek_moment', 'vertrek_spoor_real', 'Verdeling']
        
        titleColumnsOverstapper = ['stationID', 'date', 'feedingTrain', 'arrTimeFeedingTrain', 'feedingTrainTrack', \
                                   'connectingTrain', 'depTimeConnectingTrain', 'connectingTrainTrack', 'numTravelers']
        
        dataTypes = {'StationID':int, 'aankomst_verkeersdatum':str, 'aankomst_treinnummer':int, 'aankomst_moment':str, \
            'aankomst_spoor_real':str, 'vertrek_treinnummer':int, 'vertrek_moment':str, 'vertrek_spoor_real':str, \
            'Verdeling':float}
        
        #read current transfer passenger file and rename headers
        overstapperRaw = pd.read_csv(overstapperFilePath, usecols=relevantColumnsOverstapper, dtype=dataTypes)
        
        overstapperRaw.columns = titleColumnsOverstapper
        
        overstapperRawDataFiltered = overstapperRaw.loc[ (overstapperRaw['date'] == self.dayCaseStudyString) &\
            (overstapperRaw["feedingTrain"].isin(trentoTrains.relevantTrainSet) | overstapperRaw["connectingTrain"].isin(trentoTrains.relevantTrainSet) ) ]
        
        return overstapperRawDataFiltered
                
    ## Import Overstappers            
    def importOverstapper(self, trentoTrains):
        
        for overstapperFilePath in Parameter.overstapperFiles:
            
            overstapperRawDataFiltered = self.loadOverstapperData(overstapperFilePath, trentoTrains)
            
            for _, overstapperEntry in overstapperRawDataFiltered.iterrows():
                
                stationID = overstapperEntry["stationID"]
                feedingTrainNumber = overstapperEntry["feedingTrain"]
                connectingTrainNumber = overstapperEntry["connectingTrain"]
                numTravelers = overstapperEntry["numTravelers"]
                
                stationName = Parameter.stationNameDict[stationID]
                
                #at least one of the two trains should already exist
                #(it is unlikely that only transfer passengers use a train)
                assert( feedingTrainNumber in self.trainDict.keys() or connectingTrainNumber in self.trainDict.keys())
                
                if feedingTrainNumber in self.trainDict.keys():
                    
                    #check if feeding train is served by modeled platform
                    if stationName in trentoTrains.trainDict[feedingTrainNumber].stationNameSequence:
                        feedingTrain = self.trainDict[feedingTrainNumber]
                        feedingTrain.addAlightTransfer(stationName, numTravelers)
                    
                if connectingTrainNumber in self.trainDict.keys():
                    
                    #check if connecting train is served by modeled platform
                    if stationName in trentoTrains.trainDict[connectingTrainNumber].stationNameSequence:
                        connectingTrain = self.trainDict[connectingTrainNumber]
                        connectingTrain.addBoardTransfer(stationName, numTravelers)
    
    def loadRidershipData(self, ridershipFilePath, trentoTrains):
        
        relevantColumnsRidership = ['av_verkeersdatum', 'Treinnummer', 'aankomst_ID', 'Aantal_reizigers']
        titleColumnsRidership = ['date', 'trainNumber', 'destStationID', 'ridership']
        dataTypes = {'av_verkeersdatum':str, 'Treinnummer':int, 'aankomst_ID':int, 'Aantal_reizigers':float}
        
        #load ridership data and rename headers
        ridershipRaw = pd.read_csv(ridershipFilePath, usecols=relevantColumnsRidership, dtype=dataTypes)
        ridershipRaw.columns = titleColumnsRidership
         
        ridershipData = ridershipRaw.loc[ (ridershipRaw['date'] == self.dayCaseStudyString) &\
            ridershipRaw['trainNumber'].isin(trentoTrains.relevantTrainSet) ]
        
        return ridershipData
        
    ## Import Ridership
    def importRidership(self, trentoTrains):
        
        for ridershipFilePath in Parameter.ridershipFiles:
            
            ridershipData = self.loadRidershipData(ridershipFilePath, trentoTrains)
            
            #the relevant ridership data should not be empty
            assert( len(ridershipData) >= 0)
             
            for _, ridershipEntry in ridershipData.iterrows():
                
                trainNumber = ridershipEntry["trainNumber"]
                stationName = Parameter.stationNameDict[ridershipEntry["destStationID"]]

                #check if train is served by modeled platform, otherwise skip
                if stationName not in trentoTrains.trainDict[trainNumber].stationNameSequence:
                    #skip current ridership entry                    
                    continue
                
                ridership = ridershipEntry["ridership"]
                
                            
                if Parameter.showWarnings and not (ridership > 0):
                    print("Train %d has invalid ridership (%s) towards %s." % (trainNumber,ridership,stationName))
                
                assert(trainNumber in self.trainDict.keys()), "Train %s missing" % trainNumber
                train = self.trainDict[trainNumber]
                train.addRidershipTowards(stationName, ridership)
            
    def computeODRatios(self):
        #compute OD ratio for each train        
        for train in self.trainDict.values():
            train.computeODRatios()
            
    def synthesizeOneLegTravelers(self, trentoTrains):
        
        for inUitFilePath in Parameter.inUitFiles:
            
            inUitRawDataFiltered = self.loadInUitData(inUitFilePath, trentoTrains)
            
            for _, inUitEntry in inUitRawDataFiltered.iterrows():
                        
                stationID = inUitEntry["stationID"]
                gateNode = inUitEntry["gateNode"]
                trainNumber = inUitEntry["trainNumber"]
                inOut = inUitEntry["InOut"]
                numTravelers = inUitEntry["numTravelers"]
                gateTimeStampRaw = datetime.strptime( inUitEntry["gateTimeStamp"] , '%Y-%m-%dT%H:%M:%S' )
                gateTime = (gateTimeStampRaw - self.midnightCaseStudy).total_seconds()
                
                stationName = Parameter.stationNameDict[stationID]
                
                train = self.trainDict[trainNumber]
                trentoTrain = trentoTrains.trainDict[trainNumber]
                
                #check if train serves any relevant platform
                if stationName in trentoTrain.stationNameSequence:
                    
                    if train.corridorFlag:
                        
                        while ( numTravelers > random() ):
                            numTravelers -= 1
                            
                            #consider boarding, outgoing passengers
                            if inOut == "I":
                                origTime = gateTime
                                origNode = gateNode
                                destStation = train.sampleDestination(stationName)
                                
                                if destStation in Parameter.stationSet:
                                    
                                    if train.transferAtDestination(destStation):
                                        #if pedestrian is sampled to transfer, then it is contained in
                                        #the overstapper data, and generated there. Skip here
                                        continue
                                    else:
                                        #need to draw check out node
                                        destNode = train.chooseExitGate(destStation)
                                        
                                else:
                                    assert(destStation == "downstream")
                                    destNode = Parameter.downstreamNode
                                
                                #add traveler to OD table for validation   
                                train.addSynthesizedPassenger(stationName, destStation)
                            
                            #alighting passengers
                            else:
                                assert(inOut == "U")
                                origStation = train.sampleOrigin(stationName)
                                
                                if origStation in Parameter.stationSet:
                                    #pedestrian stemming from another implemented station are
                                    #already considered there as boarding passengers.
                                    #Skip to avoid double counting.
                                    continue
                                
                                else:
                                    #only keep travelers generated upstream
                                    assert(origStation == "upstream")
                                    
                                    origNode = Parameter.upstreamNode
                                    origTime = 0
                                    destNode = gateNode
                                
                                #add traveler to OD table for validation
                                train.addSynthesizedPassenger(origStation, stationName)
                             
                            curTraveler = RocktTraveler(origNode, destNode, origTime, trainNumber)
                            self.travelerSet.add(curTraveler)
                            
                            
                    else:
                        #train stopping at just one or two stations (not serving corridor)
                        
                        while ( numTravelers > random() ):
                            numTravelers -= 1
                            
                            #boarding, outgoing passengers
                            if inOut == "I":
                                origNode = gateNode
                                origTime = gateTime
                                destNode = Parameter.downstreamNode
                                
                                #add traveler to OD table for validation
                                train.addSynthesizedPassenger(stationName, "downstream")
                                
                            #alighting, incoming passengers    
                            elif inOut == "U":
                                origNode = Parameter.upstreamNode
                                origTime = 0
                                destNode = gateNode
                                
                                #add traveler to OD table for validation
                                train.addSynthesizedPassenger("upstream", stationName)
                                                             
                            curTraveler = RocktTraveler(origNode, destNode, origTime, trainNumber)
                            self.travelerSet.add(curTraveler)
    
    # POPULATION SYNTHESIS FROM OVERSTAPPER DATA
    def synthesizeTwoLegTravelers(self, trentoTrains):
        
        for overstapperFilePath in Parameter.overstapperFiles:
            
            overstapperRawDataFiltered = self.loadOverstapperData(overstapperFilePath, trentoTrains)
            
            for _, overstapperEntry in overstapperRawDataFiltered.iterrows():
            
                stationID = overstapperEntry["stationID"]
                feedingTrainNumber = overstapperEntry["feedingTrain"]
                connectingTrainNumber = overstapperEntry["connectingTrain"]
                arrTimeFeedingTrainRaw = overstapperEntry["arrTimeFeedingTrain"]
                numTravelers = overstapperEntry["numTravelers"]
                
                transferStation = Parameter.stationNameDict[stationID]
                
                feedingTrainModeled = False
                connectingTrainModeled = False
                
                #feeding train in trento train dict if served by at least one relevant platform
                if feedingTrainNumber in trentoTrains.trainDict.keys():
                    trentoFeedingTrain = trentoTrains.trainDict[feedingTrainNumber]
                    
                    #check if train served by modeled platform in current station
                    if transferStation in trentoFeedingTrain.stationNameSequence:
                        assert(feedingTrainNumber in self.trainDict), "Train %s unknown in ROCKT InUit data." % feedingTrainNumber
                        
                        feedingTrain = self.trainDict[feedingTrainNumber]
                        feedingTrainModeled = True
                    
                #connecting train in trento train dict if served by at least one relevant platform    
                if connectingTrainNumber in trentoTrains.trainDict.keys():
                    trentoConnectingTrain = trentoTrains.trainDict[connectingTrainNumber]
                    
                    #consider connecting train only if also served by modeled platform in current station
                    if transferStation in trentoConnectingTrain.stationNameSequence:
                        assert(connectingTrainNumber in self.trainDict), "Train %s unknown in ROCKT InUit data." % connectingTrainNumber
                        
                        connectingTrain = self.trainDict[connectingTrainNumber]
                        connectingTrainModeled = True
                
                #both trains served on modeled platform
                if (feedingTrainModeled and connectingTrainModeled):
                
                    #synthesize individual travelers
                    while ( numTravelers > random() ):
                        
                        numTravelers -= 1
                        
                        #draw origin node and time
                        origTime, origNode, origStation = feedingTrain.sampleOriginStationAndEntranceGate(transferStation)
                        
                        #draw destination node
                        destNode, destStation = connectingTrain.sampleDestinationStationAndExitGate(transferStation)    
                        
                        curTraveler = RocktTraveler(origNode, destNode, origTime, [feedingTrainNumber,connectingTrainNumber])
                        curTraveler.setTransferStation(transferStation)
                        
                        self.travelerSet.add(curTraveler)
                        
                        #add two travelers to OD table for validation
                        feedingTrain.addSynthesizedPassenger(origStation, transferStation)
                        connectingTrain.addSynthesizedPassenger(transferStation, destStation)
                                            
                        
                #only feeding train served by modeled platform:
                #consider as incoming passenger (instead of transfer)
                elif feedingTrainModeled:
                    
                    #synthesize individual travelers
                    while ( numTravelers > random() ):
                        
                        numTravelers -= 1
                        
                        #draw origin node and time
                        origTime, origNode, origStation = feedingTrain.sampleOriginStationAndEntranceGate(transferStation)
                        
                        ##draw exit gate in transfer station which becomes final destination
                        #destNode = feedingTrain.chooseExitGate(transferStation)
                        
                        #destNode set to virtual transfer desk asking as gate
                        destNode = weightedChoice(Parameter.transferGate[transferStation])
                                        
                        curTraveler = RocktTraveler(origNode, destNode, origTime, feedingTrainNumber)
                        self.travelerSet.add(curTraveler)
                        
                        #add traveler to OD table for validation
                        feedingTrain.addSynthesizedPassenger(origStation, transferStation)
                                            
                #only connecting train served by modeled platform:
                #consider as outgoing passenger (instead of transfer)
                elif connectingTrainModeled:
                    
                    arrTimeFeedingTrain = datetime.strptime( arrTimeFeedingTrainRaw , '%Y-%m-%dT%H:%M:%S' )
                    origTime = (arrTimeFeedingTrain - self.midnightCaseStudy).total_seconds()
                    assert(origTime > 0)
                    
                    #synthesize individual travelers
                    while ( numTravelers > random() ):
                        
                        numTravelers -= 1
                    
                        ##draw entrance gate
                        #origNode = connectingTrain.chooseEntranceGate(transferStation)
                        origNode = weightedChoice(Parameter.transferGate[transferStation])
                        
                        #draw destination station and node
                        destNode, destStation = connectingTrain.sampleDestinationStationAndExitGate(transferStation)
                            
                        curTraveler = RocktTraveler(origNode, destNode, origTime, connectingTrainNumber)
                        self.travelerSet.add(curTraveler)
                        
                        #add traveler to OD table for validation
                        connectingTrain.addSynthesizedPassenger(transferStation, destStation)
                        
                #neither feeding nor connecting train served by modeled platform:
                else:
                    #discard concerned passengers
                    continue
                
#     def checkConsisteny(self, trentoTrains):
#         
#         print("\nConsistency Check:")
#         
#         boardInTrainStationDict = dict()
#         alightOutTrainStationDict = dict()
#         
#         boardTransferTrainStationDict = dict()
#         alightTransferTrainStationDict = dict()
#         
#         boardAuxiliaryTrainStationDict = dict()
#         alightAuxiliaryTrainStationDict = dict()
#         
#         gateValidationDict = {'61001':'AsdZ-Minerva', '61002':'AsdZ-Minerva', '61003':'AsdZ-Minerva'}
#         
#         gateValidationFlow = dict()
#        
#         
#         for traveler in self.travelerSet:
#             
#             origNode = traveler.origNode[1:]
#             destNode = traveler.destNode[1:]
#             
#             depTime = traveler.depTime
#             
#             trainList = traveler.trainList
#             transferStation = traveler.transferStation
#             
#             origTrain = trainList[0]
#             destTrain = trainList[-1]
#                         
#             if origNode in gateValidationDict.keys():
#                 
#                 validationGroup = gateValidationDict[origNode]
#                 
#                 if validationGroup not in gateValidationFlow:
#                     gateValidationFlow[validationGroup] = dict()
#                                 
#                 if depTime not in gateValidationFlow[validationGroup].keys():
#                     gateValidationFlow[validationGroup][depTime] = 0
#                     
#                 gateValidationFlow[validationGroup][depTime] += 1
#                 
#         
#             if origTrain not in boardInTrainStationDict.keys():
#                 boardInTrainStationDict[origTrain] = dict()
#                 boardAuxiliaryTrainStationDict[origTrain] = dict()
#             
#             boardInStationDict = boardInTrainStationDict[origTrain]
#             boardAuxiliaryStationDict = boardAuxiliaryTrainStationDict[origTrain]
#             
#             auxiliary = False
#             
#             if origNode == 'up':
#                 origStation = 'upstream'
#             elif origNode[0:5] == 'Trans':
#                 auxiliary = True
#                 statNameRaw = origNode[5:]
#                 
#                 if statNameRaw in Parameter.stationNameDict.values():
#                     origStation=statNameRaw
#                 else:
#                     assert(statNameRaw[:-1] == 'Utrecht'), "invalid station name: %s" % statNameRaw[:-1]
#                     origStation = 'Utrecht'
#             
#             elif int(origNode[0:3]) in Parameter.stationNameDict.keys():
#                 origStation = Parameter.stationNameDict[ int(origNode[0:3]) ]
#                 
#             elif int(origNode[0:2]) in Parameter.stationNameDict.keys():
#                 origStation = Parameter.stationNameDict[ int(origNode[0:2]) ]
#             
#             else:
#                 print("Could not identify origin station (%s)" % origNode)
#                 
#         
#             if origStation not in boardInStationDict:
#                 boardInStationDict[origStation] = 0
#                 boardAuxiliaryStationDict[origStation] = 0
#             
#             if auxiliary == False:
#                 boardInStationDict[origStation] += 1
#             else:
#                 boardAuxiliaryStationDict[origStation] += 1
#             
#             if destTrain not in alightOutTrainStationDict.keys():
#                 alightOutTrainStationDict[destTrain] = dict()
#                 alightAuxiliaryTrainStationDict[destTrain] = dict()
#                 
#             alightOutStationDict = alightOutTrainStationDict[destTrain]
#             alightAuxiliaryStationDict = alightAuxiliaryTrainStationDict[destTrain]
#             
#             auxiliary=False
#             
#             if destNode == 'down':
#                 destStation = 'downstream'
#             elif destNode[0:5] == 'Trans':
#                 auxiliary = True
#                 statNameRaw = destNode[5:]
#                 
#                 if statNameRaw in Parameter.stationNameDict.values():
#                     destStation=statNameRaw
#                 else:
#                     assert(statNameRaw[:-1] == 'Utrecht'), "invalid station name: %s" % statNameRaw[:-1]
#                     destStation = 'Utrecht'
#             elif int(destNode[0:3]) in Parameter.stationNameDict.keys():
#                     destStation = Parameter.stationNameDict[ int(destNode[0:3]) ]
#             
#             elif int(destNode[0:2]) in Parameter.stationNameDict.keys():
#                     destStation = Parameter.stationNameDict[ int(destNode[0:2]) ]
#                     
#             else:
#                 print("Could not identify destination station (%s)" % destNode)
#                     
#             
#             if destStation not in alightOutStationDict:
#                 alightOutStationDict[destStation] = 0
#                 alightAuxiliaryStationDict[destStation] = 0
#             
#             if auxiliary == False:
#                 alightOutStationDict[destStation] += 1
#             else:
#                 alightAuxiliaryStationDict[destStation] += 1
#             
#             if transferStation is not None:
#                 assert(len(trainList) == 2)
#                 
#                 if origTrain not in alightTransferTrainStationDict:
#                     alightTransferTrainStationDict[origTrain] = dict()
#                     
#                 alightTransferStationDict = alightTransferTrainStationDict[origTrain]
#                 
#                 if transferStation not in alightTransferStationDict.keys():
#                     alightTransferStationDict[transferStation] = 0
#                 
#                 alightTransferStationDict[transferStation] += 1
#                 
#                 
#                 if destTrain not in boardTransferTrainStationDict:
#                     boardTransferTrainStationDict[destTrain] = dict()
#                     
#                 boardTransferStationDict = boardTransferTrainStationDict[destTrain]
#                 
#                 if transferStation not in boardTransferStationDict.keys():
#                     boardTransferStationDict[transferStation] = 0
#                     
#                 boardTransferStationDict[transferStation] += 1
#         
#         self.consistencyProtocol = dict()
#         
#         for trainNumber, train in self.trainDict.items():
#             
#             curStr = "%d (boardOut/alightIn/boardTrans/alightTrans):" % trainNumber
#             
#             for stationName in Parameter.stationNameDict.values():
#                 curStr += " %s: " % stationName
#                 
#                 compare boardings
#                 if stationName in train.boardOutgoing.keys():
#                     boardOutRaw =  train.boardOutgoing[stationName]
#                     
#                     if trainNumber in boardInTrainStationDict.keys() and stationName in boardInTrainStationDict[trainNumber].keys():
#                         boardOutSynth = boardInTrainStationDict[trainNumber][stationName]
#                     else:
#                         boardOutSynth = 0
#                     
#                     curStr += "%+.1f%% (%d instead of %.1f) / " % ((boardOutSynth/boardOutRaw-1)*100,boardOutSynth,boardOutRaw)
#                 
#                 compare alightings
#                 if stationName in train.alightIncoming.keys():
#                     alightInRaw =  train.alightIncoming[stationName]
#                     
#                     if trainNumber in alightOutTrainStationDict.keys() and stationName in alightOutTrainStationDict[trainNumber].keys():
#                         alightInSynth = alightOutTrainStationDict[trainNumber][stationName]
#                     else:
#                         alightInSynth = 0
#                     
#                     curStr += "%+.1f%% (%d instead of %.1f) / " % ((alightInSynth/alightInRaw-1)*100,alightInSynth,alightInRaw)
#                 
#                 compare transfer boardings
#                 if stationName in train.boardTransfer.keys():
#                     boardTransferRaw = train.boardTransfer[stationName]
#                     
#                     boardTransferSynth = 0
#                     
#                     if trainNumber in boardTransferTrainStationDict.keys() and stationName in boardTransferTrainStationDict[trainNumber].keys():
#                         boardTransferSynth += boardTransferTrainStationDict[trainNumber][stationName]
#                     
#                     if trainNumber in boardAuxiliaryTrainStationDict.keys() and stationName in boardAuxiliaryTrainStationDict[trainNumber].keys():
#                         boardTransferSynth += boardAuxiliaryTrainStationDict[trainNumber][stationName]
#                     
#                     curStr += "%+.1f%% (%d instead of %.1f) / " % ((boardTransferSynth/boardTransferRaw-1)*100,boardTransferSynth,boardTransferRaw)
#                     
#                 compare transfer alightings
#                 if stationName in train.alightTransfer.keys():
#                     alightTransferRaw = train.alightTransfer[stationName]
#                     
#                     alightTransferSynth = 0
#                     
#                     if trainNumber in alightTransferTrainStationDict.keys() and stationName in alightTransferTrainStationDict[trainNumber].keys():
#                         alightTransferSynth += alightTransferTrainStationDict[trainNumber][stationName]
#                     
#                     if trainNumber in alightAuxiliaryTrainStationDict.keys() and stationName in alightAuxiliaryTrainStationDict[trainNumber].keys():
#                         alightTransferSynth += alightAuxiliaryTrainStationDict[trainNumber][stationName]
#                     
#                     curStr += "%+.1f%% (%d instead of %.1f)" % ((alightTransferSynth/alightTransferRaw-1)*100,alightTransferSynth,alightTransferRaw)
#             
#             self.consistencyProtocol[trainNumber] = curStr
#             
#         print(self.consistencyProtocol)
#                 
#         for validatorName, validatorFlowDict in gateValidationFlow.items():
#             
#             print("checking gate in-flow at %s [paused]" % validatorName)
#         
#             timeStamps,flowObs = zip(*( sorted( validatorFlowDict.items() ) ))
#             
#             cumFlow = np.cumsum(flowObs)
#             
#             plotting cumulative flow
#             figCum, axCum = plt.subplots()
#             
#             plt.ylabel('cumulative flow')
#             plt.title(validatorName)
#             
#             plt.step(timeStamps, cumFlow, where='post', label='synthesizedDemand', color='blue')
#             
#             plt.legend()
#             
#             plt.show()