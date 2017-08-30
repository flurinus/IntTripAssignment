import re
import math
import pandas as pd
from datetime import datetime, timedelta
from parameter import Parameter
from trentoTrain import TrentoTrain

class TrentoData(object):
    '''
    Reads and stores train information from NS' TRENTO train database
    '''

    def __init__(self, param):
        #retrieve start and end date
        self.dateStart = param.dateStart 
        self.dateEnd = param.dateEnd
        self.midnightCaseStudy = param.midnightCaseStudy
        self.dayCaseStudyString = param.dayCaseStudyString
        
        #get set of relevant trains
        self.relevantTrainSet = self.getRelevantTrainSet()
        
        #read trento data for a set of trains contained by trainSet
        self.trainDict = self.readTrento()
        
    def __repr__(self):
        
        trentoDataStr = "\nRelevant TRENTO trains:\n"
        
        for trainNumber, train in self.trainDict.items():
            trentoDataStr += "%s: %s\n" % (trainNumber,train)
            
        trentoDataStr += "(total: %d trains)\n" % len(self.trainDict)
            
        return trentoDataStr
        
    def getRelevantTrainSet(self):
        #define relevant columns of Trento data set
        relevantColumnsTrento = ['Vkdatum', 'Treinnr', 'Drp', 'Spoor',
            'Aankomsttijd', 'Vertrektijd', 'Vgb_plan_aankomst', 'Vgb_plan_vertrek']
        titleColumnsTrento = ['dateDispatch', 'trainNumber', 'stationAbbreviation', 'trackNumber',
            'arrTimeReal', 'depTimeReal', 'arrTimeSched', 'depTimeSched']
        
        #set of relevant train numbers
        trainNumberSet = set()
        
        for trentoFilePath in Parameter.trentoFiles:
            #load relevant columns
            trentoFull = pd.read_csv(trentoFilePath, usecols=relevantColumnsTrento)
            
            #rename headers
            trentoFull.columns = titleColumnsTrento
            
            #retain data for case study date
            trentoData = trentoFull.loc[ ( trentoFull['dateDispatch'] == self.dayCaseStudyString ) &
                           ( trentoFull['stationAbbreviation'].isin( Parameter.stationAbbreviationDict.keys() ) ) ]
            
            for _, trentoEntry in trentoData.iterrows():
                
                stationID = Parameter.stationAbbreviationDict[ trentoEntry["stationAbbreviation"] ]
                stationName = Parameter.stationNameDict[stationID]
                
                #get track number in integer format
                trackNumberRaw = trentoEntry["trackNumber"]
                if isinstance(trackNumberRaw,int):
                    trackNumber = trackNumberRaw
                else:
                    #get first integer from track number
                    trackNumber = int( re.findall(r'\d+', trackNumberRaw)[0] )
                
                #skip to next entry unless train served by considered platform
                if not (trackNumber in Parameter.tracksConsidered[stationName]):
                    continue
                 
                #arrival and departure date: use realized if available, otherwise scheduled time
                if isinstance(trentoEntry['arrTimeReal'], str):
                    arrDate = datetime.strptime( trentoEntry['arrTimeReal'] , '%Y-%m-%d %H:%M:%S' )
                elif isinstance(trentoEntry['arrTimeSched'], str):
                    arrDate = datetime.strptime( trentoEntry['arrTimeSched'] , '%Y-%m-%d %H:%M:%S' )
                else:
                    arrDate = None
                
                #skip to next entry if current train movement is too late
                if (arrDate is not None) and (self.dateEnd < arrDate):
                    continue
                    
                if isinstance( trentoEntry['depTimeReal'] , str):
                    depDate = datetime.strptime( trentoEntry['depTimeReal'] , '%Y-%m-%d %H:%M:%S' )
                elif isinstance( trentoEntry['depTimeSched'] , str):
                    depDate = datetime.strptime( trentoEntry['depTimeSched'] , '%Y-%m-%d %H:%M:%S' )
                else:
                    depDate = None
                
                #skip to next entry if current train movement is too early
                if (depDate is not None) and (depDate < self.dateStart):
                    #if train departs before simulation starts, skip train
                    continue
                
                #if no arrival, and departure time outside time window: skip train
                if arrDate is None and not (self.dateStart <= depDate <= self.dateEnd):
                    continue
                
                #if no departure, and arrival time outside time window: skip train
                if depDate is None and not (self.dateStart <= arrDate <= self.dateEnd):
                    continue
                 
                #train movement is within considered time interval and served by relevant platform
                trainNumber = trentoEntry["trainNumber"]
                
                trainNumberSet.add(trainNumber)
                
        return trainNumberSet
     
    #provide Trento trains in format readable for pedQN
    def getTrainDict(self):
        return self.trainDict
    
    def readTrento(self):
        relevantColumnsTrento = ['Vkdatum', 'Treinnr', 'Drp', 'Spoor',
            'Mat_a_soort', 'Mat_a_bakken', 'Mat_a_lengte', 'Mat_v_soort', 'Mat_v_bakken', 'Mat_v_lengte',
            'Aankomsttijd', 'Vertrektijd', 'Vgb_plan_aankomst', 'Vgb_plan_vertrek']
        
        titleColumnsTrento = ['dateDispatch', 'trainNumber', 'stationAbbreviation', 'trackNumber',
            'rollingStockTypeArr', 'numCarsArr', 'trainLengthArr', 'rollingStockTypeDep', 'numCarsDep', 'trainLengthDep',
            'arrTimeReal', 'depTimeReal', 'arrTimeSched', 'depTimeSched']
        
        #list of dataframes generated from reading trento raw files
        trentoDataFrames = list()
        
        for trentoFilePath in Parameter.trentoFiles:
            #read current trento file and rename headers
            trentoFull = pd.read_csv(trentoFilePath, usecols=relevantColumnsTrento)
            trentoFull.columns = titleColumnsTrento
                
            #select entries corresponding to case study date and train list
            trentoDataInstance = trentoFull.loc[ ( trentoFull['dateDispatch'] == self.dayCaseStudyString ) &
                               ( trentoFull['trainNumber'].isin( self.relevantTrainSet ) ) ]
            
            trentoDataFrames.append(trentoDataInstance)
            
        #concatenate various trento files into single document
        trentoData = pd.concat(trentoDataFrames, ignore_index=True)
        
        #dict of trento trains
        trentoTrainDict = dict()
    
        for trainNumber in self.relevantTrainSet:
            #retrieve TRENTO data for current train    
            curTrainData = trentoData.loc[ trentoData['trainNumber'] == trainNumber ].sort_values(['depTimeSched'])
            
            #check if train exists in TRENTO database
            assert(not curTrainData.empty)
                
            #infer scheduled and realized train arrival/departure times
            arrTimeReal = list()
            depTimeReal = list()
            arrTimeSched = list()
            depTimeSched = list()
            platformSequence = list()
            stationNameSequence = list()
            
            #train-specific information
            rollingStockSet = set()
            numCarsSet = set()
            trainLengthSet = set()
            
            #valid train flag: true if stops at one or more modeled platforms
            validTrain = False
                
            for _, entry  in curTrainData.iterrows():
                
                stationAbbreviation = entry['stationAbbreviation']
                stationID = Parameter.stationAbbreviationDict[stationAbbreviation]
                stationName = Parameter.stationNameDict[stationID] 
                
                #get track number in integer format
                trackNumberRaw = entry["trackNumber"]
                if isinstance(trackNumberRaw,int):
                    trackNumber = trackNumberRaw
                else:
                    #get first integer from track number
                    trackNumber = int( re.findall(r'\d+', trackNumberRaw)[0] )
                
                platform = '%s%s%s' % (stationName[0], 'P', trackNumber )
                
                #if current stop of train outside the modeled parameter, skip stop
                if trackNumber not in Parameter.tracksConsidered[stationName]:
                    #if Parameter.showWarnings:
                    #    print("Warning: Train %s served by unmodeled platform (%s instead of %s)" %\
                    #        (trainNumber, platform, Parameter.tracksConsidered[stationName]))
                    #skip current stop
                    continue
                
                #train neither arrives or departs
                if not (isinstance(entry['arrTimeReal'],str) or isinstance(entry['depTimeReal'],str)):
                    if Parameter.showWarnings:
                        print("Train %s neither departs nor arrives in %s. " % (trainNumber,stationName), end='')
                        print("Track: %s, depReal: %s; arrReal: %s; depSched: %s; arrSched: %s" % (trackNumber, entry['depTimeReal'], entry['arrTimeReal'], entry['depTimeSched'], entry['arrTimeSched']) )
                    
                    #skip current stop
                    continue
                
                validTrain = True
                
                trainOnlyDeparts = False
                
                if isinstance(entry['arrTimeReal'],str):
                    arrReal = datetime.strptime( entry['arrTimeReal'] , '%Y-%m-%d %H:%M:%S' )
                    arrSched = datetime.strptime( entry['arrTimeSched'] , '%Y-%m-%d %H:%M:%S' )
                
                #train only departs
                else:
                    if Parameter.showWarnings:
                        print("Warning: Train %s only departs" % trainNumber)
                        
                    trainOnlyDeparts = True
                    assert(isinstance(entry['arrTimeReal'],float))
                    assert( math.isnan(entry['arrTimeReal']) )
                    
                    #set arbitrary arrival time: 10 min before departure
                    arrReal = datetime.strptime( entry['depTimeReal'] , '%Y-%m-%d %H:%M:%S' ) - timedelta(minutes=10)
                    arrSched = datetime.strptime( entry['depTimeSched'] , '%Y-%m-%d %H:%M:%S' ) - timedelta(minutes=10)
                
                if isinstance(entry['depTimeReal'],str):    
                    depReal = datetime.strptime( entry['depTimeReal'] , '%Y-%m-%d %H:%M:%S' )
                    depSched = datetime.strptime( entry['depTimeSched'] , '%Y-%m-%d %H:%M:%S' )
                
                #train only arrives
                else:
                    if Parameter.showWarnings:
                        print("Warning: Train %s only arrives" % trainNumber)
                    
                    assert(isinstance(entry['depTimeReal'],float))
                    assert( math.isnan(entry['depTimeReal']) )
                    
                    #set arbitrary departure time: 10 min after arrival
                    depReal = datetime.strptime( entry['arrTimeReal'] , '%Y-%m-%d %H:%M:%S' ) + timedelta(minutes=10)
                    depSched = datetime.strptime( entry['arrTimeReal'] , '%Y-%m-%d %H:%M:%S' ) + timedelta(minutes=10)
                                
                platformSequence.append(platform)
                stationNameSequence.append(stationName)
                
                arrTimeReal.append( (arrReal - self.midnightCaseStudy).total_seconds() )
                depTimeReal.append( (depReal - self.midnightCaseStudy).total_seconds() )
                arrTimeSched.append( (arrSched - self.midnightCaseStudy).total_seconds() )
                depTimeSched.append( (depSched - self.midnightCaseStudy).total_seconds() )
                
                if trainOnlyDeparts:
                    rollingStockSet.add( entry['rollingStockTypeDep'] )
                    numCarsSet.add( entry['numCarsDep'] )
                    trainLengthSet.add( entry['trainLengthDep'] )
                else:
                    rollingStockSet.add( entry['rollingStockTypeArr'] )
                    numCarsSet.add( entry['numCarsArr'] )
                    trainLengthSet.add( entry['trainLengthArr'] )
                    
            #if current train is invalid, skip
            if not validTrain:
                if Parameter.showWarnings:
                    print("Skipping train %s. No valid stops found." % trainNumber)
                    
                continue
                    
            #check if rolling stock is consistent across stations
            assert( len(rollingStockSet) == 1 ), "train %s: rolling stock changes during operation: %s" % (trainNumber, rollingStockSet)
            assert( len(numCarsSet) == 1), "train %s: number of cars changes during operation: %s" % (trainNumber, numCarsSet)
            assert( len(trainLengthSet) == 1), "train %s: train length changes during operation: %s" % (trainNumber, trainLengthSet)
            
            rollingStockTypeSeq = rollingStockSet.pop()
            numCars = int(numCarsSet.pop())
            #trainLength = float( trainLengthSet.pop().replace(',','.') )
            trainLength = trainLengthSet.pop()
        
            
            #determine rolling stock type and infer capacity
            rollingStockTypeSet = set(rollingStockTypeSeq.split())
            rollingStockBaseType = next(iter(rollingStockTypeSet))
            
            #check if train is homogeneous (only one rolling stock type)
            assert( 1==len(rollingStockTypeSet) ), "train %s: rolling stock type varies during operation: %s" % \
                (trainNumber, rollingStockTypeSeq)
            assert( rollingStockBaseType in Parameter.passengerCarCapacity.keys() ), \
                "train %s: rolling stock type '%s' not in rolling stock catalog %s" %\
                (trainNumber, rollingStockBaseType, set(Parameter.passengerCarCapacity.keys()))
                
            
            trainKey= (rollingStockBaseType, numCars)
            if trainKey in Parameter.trainLengthDict:
                trainLengthManual = Parameter.trainLengthDict[rollingStockBaseType, numCars]
                #print("trainLengthNew: %s" % trainLengthNew)
            else:
                print("trainKey (%s,%s) missing" % trainKey)
                
            if not (0.9*trainLengthManual < trainLength < 1.1*trainLengthManual):
                if Parameter.showWarnings:
                    print("Warning: Train length reported by Trento (%s m) differs substantially from rolling stock catalog (%s m). Using the latter." %\
                          (trainLength, trainLengthManual) )
                
                trainLength = trainLengthManual
            
            carCapacity = Parameter.passengerCarCapacity[rollingStockBaseType]
            
            #store train in local TRENTO database
            curTrain = TrentoTrain(platformSequence, stationNameSequence, arrTimeSched, depTimeSched, arrTimeReal, depTimeReal,
                                   rollingStockBaseType, numCars, carCapacity, trainLength)
            
            trentoTrainDict[trainNumber] = curTrain
        
        return trentoTrainDict;

