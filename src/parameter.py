import datetime
import os
import shutil


class Parameter(object):
    
    showWarnings = False
    postProcess = True
    postProcessOnly = True
    scenarioName = 'calib_'
    postProcessFolder = 'postprocessing'
    
    #date of case study (required e.g. for reading from ROCKT/TRENTO database)
    #dateCaseStudy = '2015-09-01'
    timeCaseStudyStart = '06:30:00' 
    timeCaseStudyEnd = '09:30:00'
    
    #standard deviation of free-flow speed (for sampling of speed multiplier)
    freeFlowSpeedSigma = 0.215
    
    #in case of missed train, increase speed by factor until max speed
    maxSpeedMultiplier = 2 #ALTERNATIVE: 1.5 1%-quantile norm(loc=1,scale=0.215).ppf(0.99)
    speedMultiplierIncrease = 1.1 #increase speed by 10%
    
    transferGate = {'AsdZ': {'TransAsdZ': 1.0}, 'Bijlmer': {'TransBijlmer': 1.0},
                    'Utrecht': {'TransUtrecht': 1.0},
                    'Schiphol': {'TransSchiphol': 1.0} }
    
    densitySpeedRelationship = {'walkway':{'basicFreeSpeed':1.41,'shapeParam':1.913, 'jamDensity':5.4},
                 'bidirWalkway':{'basicFreeSpeed':1.41,'shapeParam':1.913, 'jamDensity':5.4},
             'stairwayUp':{'basicFreeSpeed':0.610, 'shapeParam':3.722, 'jamDensity':5.4},
             'stairwayDown':{'basicFreeSpeed':0.694, 'shapeParam':3.802, 'jamDensity':5.4},
             'escalatorUp':{'basicFreeSpeed':0.893, 'shapeParam':15.30, 'jamDensity':5.4, 'mechSpeed':0.5, 'walkProb':0.3},
             'escalatorDown':{'basicFreeSpeed':1.052, 'shapeParam':5.965, 'jamDensity':5.4, 'mechSpeed':0.5, 'walkProb':0.3}
            }
    
    minSpeed = 0.1 #to avoid gridlock
    interfaceTimeInterval = 5

    maxFacilityDensity = {'horizontal':{'maxDensity':5.4},
             'stairway':{'maxDensity':5.4},
             'escalator':{'maxDensity':5.4},
            }
    
    edgeAreaType = {'walkway':'horizontal','bidirWalkway':'horizontal','stairwayUp':'stairway','stairwayDown':'stairway','escalatorUp':'escalator','escalatorDown':'escalator'}
        
    numSimRuns = 8
    numParallelRuns = 8
    learningInstances = 250 #should be larger than the smallest pathSet
    finalInstances = 50 #are kept for analysis of output
    learningParam = 0.7 #see Wahba and Shalaby (2005) (parameter must be between 0 and 1)
    
    #doorServiceRateMean = 1
    
    #time for boarding/alighting per pedestrian per vehicle (typically over two doors)
    #from Wiggenrad
    boardAlightServiceTimesPerVehicle = {'ICM':0.56, 'VIRM':0.45, 'DDZ':0.45, 'SGM':0.38, 'SGMM':0.38, 'SLT':0.56, 'ICE':0.56}
    trainLengthDict = {('VIRM', 4): 108.6, ('VIRM', 8): 217.2, ('VIRM', 6): 162.1, ('VIRM', 10): 270.7,
        ('ICM', 7): 187.7, ('ICM', 11): 294.8, ('ICM', 10): 268.3, ('VIRM', 12): 324.2, ('ICM', 6): 161.2, ('ICM', 4): 107.1,
        ('ICM', 8): 214.2, ('ICM', 3): 80.6, ('ICM', 9): 241.8, ('ICM', 12): 322.4, ('SLT', 10): 169.9,
        ('SLT', 4): 69.4, ('SLT', 8): 138.8, ('SLT', 6): 100.5,
        ('SGMM',2): 52.2, ('SGMM',3): 78.7, ('SGMM',4): 104.4, ('SGMM',5): 130.9, ('SGMM',6): 157.4,
        ('DDZ',4): 101.8, ('DDZ',6): 153.88, ('DDZ',8): 203.6, ('DDZ',12): 307.76,
        ('ICE',7): 200.8}

    
    #only for debugging
    verboseOutput = False
    textOutput = False
    
    initialPotential = 1 #any arbitrary positive number
    
    costMissedTrain = 10000
    
    #value of time
    betaIVTZero = 0.006352063859513 #calibrated using survey
    #passengers waiting on lateral platform sectors may be required to walk to reach train, if train car only partially covers sector
    #penalty = (1-serviceProbability)*penaltyTrans 
    penaltyTrans = 4.1*60*betaIVTZero #transfer penalty equal to 4.1 min of IVT time
    
    #Mark Wardman & Gerard Whelan (2011), commuters
    loadFactorThresholdsSeated = [0.75, 1, 1.25, 1.5, 1.75, 2, float('Infinity')]
    loadFactorThresholdsStanding = [1.25, 1.5, 1.75, 2, float('Infinity')]
    timeMultiplierIVTSeated = {0.75:0.86, 1:0.95, 1.25:1.05, 1.5:1.16, 1.75:1.27, 2:1.40, float('Infinity'):1.55}
    timeMultiplierIVTStanding = {1.25:1.62, 1.5:1.79, 1.75:1.99, 2:2.20, float('Infinity'):2.44}
    
    timeMultiplierRailAccess = {'stairway': [(0, 3.09), (5.4, 3.09)],#(0, 4.6148), (5.4, 4.6148)],
        'escalator': [(0, 2.12), (5.4, 2.12)], #(0, 3.0876), (5.4, 3.0876)],
        'walkingHorizontal': [(0, 1.66), (1.30, 1.66), (1.35, 1.7202), (1.40, 1.7878), (1.45, 1.8613), (1.50, 1.9408), (1.55, 2.0262), (1.60, 2.1176), (1.65, 2.2149), (1.70, 2.3181), (1.75, 2.4273), (1.80, 2.5453), (5.4, 2.5453)], 
        'waitingPlatform': [(0, 1.1067), (0.5, 1.1067), (0.55, 1.1103), (0.6, 1.1192), (0.65, 1.1313), (0.7, 1.1468), (0.75, 1.1657), (0.8, 1.1878), (0.85, 1.2133), (0.9, 1.2421), (0.95, 1.2743), (1.0, 1.3097), (1.05, 1.3485), (1.1, 1.3907), (1.15, 1.4361), (1.2, 1.4849), (1.25, 1.5371), (1.3, 1.5925), (1.35, 1.6513), (1.4, 1.7134), (1.45, 1.7788), (1.5, 1.8476), (1.55, 1.9197), (1.6, 1.9951), (1.65, 2.0739), (1.7, 2.1560), (1.75, 2.2414), (1.8, 2.3240), (5.4, 2.3240)]
        }

#     loadFactorThresholdsSeated = [float('Infinity')]
#     loadFactorThresholdsStanding = [float('Infinity')]
#     timeMultiplierIVTSeated = {float('Infinity'):1}
#     timeMultiplierIVTStanding = {float('Infinity'):1}
#     
#     timeMultiplierRailAccess = {'stairway': [(0, 3.09), (5.4, 3.09)],#(0, 4.6148), (5.4, 4.6148)],
#         'escalator': [(0, 2.12), (5.4, 2.12)], #(0, 3.0876), (5.4, 3.0876)],
#         'walkingHorizontal': [(0, 1.66), (5.4, 1.66)], 
#         'waitingPlatform': [(0, 1.1067), (5.4, 1.1067)]
#         }

  
    #density-LOS relationships according to Fruin
    losWalkingFruin = [0.308, 0.431, 0.718, 1.076, 2.153, float('Infinity')]
    losWaitingFruin = [0.828, 1.076, 1.538, 3.588, 5.382, float('Infinity')]
    losStairsFruin = [0.538, 0.718, 1.076, 1.538, 2.691, float('Infinity')]
    losLevels = ['A','B','C','D','E','F']
    
    #information related to NS' TRENTO database/rolling stock catalog
    trentoFiles = {'data/Ut_trento_March2017.csv', 'data/Asb_trento_March2017.csv', 'data/Asdz_trento_March2017.csv', 'data/Shl_trento_March2017.csv'}
    
    #information related to NS ROCKT data
    inUitFiles = {'data/Ut_in_en_uit_March2017.csv', 'data/Asb_in_en_uit_March2017.csv', 'data/Asdz_in_en_uit_March2017.csv', 'data/Shl_in_en_uit_March2017.csv'}
    overstapperFiles = {'data/Ut_overstappers_March2017.csv', 'data/Asb_overstappers_March2017.csv', 'data/Asdz_overstappers_March2017.csv', 'data/Shl_overstappers_March2017.csv'}
    ridershipFiles = {'data/Ut_aantal_in_trein_March2017.csv', 'data/Asb_aantal_in_trein_March2017.csv', 'data/Asdz_aantal_in_trein_March2017.csv', 'data/Shl_aantal_in_trein_March2017.csv'}
    
    passengerCarCapacity = {'VIRM':94, 'ICM':63, 'SLT':45, 'SGM':55, 'SGMM':55, 'DDZ':84, 'ICE':65}
    
    #NS station IDs
    stationAbbreviationDict = {'UT':621, 'ASB':74, 'ASDZ':61, 'SHL':561} #abbreviations in TRENTO are capitalized
    stationNameDict = {621:'Utrecht', 74:'Bijlmer', 61:'AsdZ', 561:'Schiphol'}
    stationNameDictRev = {'Utrecht':621, 'Bijlmer':74, 'AsdZ':61, 'Schiphol':561}
    stationSet = set(stationNameDict.values())
    
    #set of valid check-in/check-out zone IDs
    rocktGateIDSetIn = {'up', 'TransUtrecht', 'TransBijlmer', 'TransAsdZ', 'TransSchiphol',
        '561001', '561002', '561003', '561004', '561005',
        '61001', '61021', '61022', '61003', '61004', '61005',
        '74001', '74002', '74003', '74004', '74005', '74006',
        '621001', '621002', '621003', '621004'}
    
    rocktGateIDSetOut = {'down', 'TransUtrecht', 'TransBijlmer', 'TransAsdZ', 'TransSchiphol',
        '561001', '561002', '561003', '561004', '561005',
        '61001', '61002', '61003', '61004', '61005',
        '74001', '74002', '74003', '74004', '74005', '74006',
        '621001', '621002', '621003', '621004'}
    
    rocktGateIDCorrectionDict = {'561--3': '561003', '561--4': '561004', 
        '061003': '61003', '061001': '61001', '061002': '61002', '061004': '61004', '061005': '61005', '061--3': '61003',
        '074001':'74001', '074002':'74002', '074003':'74003', '074004':'74004', '074005':'74005', '074006':'74006'
    }
    
    rocktInGateResampleDict = {'61002':{'61021':0.45, '61022':0.55}} #estimated based on aggregate ratio between ASE stair flow (PF2) and ROCKT check-ins at gate 61002
    rocktInGateAggregationDict = {'G61021':'G61002', 'G61022':'G61002'}
    
    utrechtCorruptedGateIDs = {'621--1', '897008', '621013', '897003', '621--2', '621--3', '294099', '074099', '053099'}
    
    utrechtGateFrequencyDict = {'621001': 0.346, '621002': 0.502, '621003': 0.128, '621004': 0.024}
    
    #relative OD fractions: computed from confidential NS OD-relation database
    #below values are aggregated and thus not confidential
    #fracUtrechtBijlmer = REMOVED
    #fracUtrechtAsdZ = REMOVED
    #fracBijlmerAsdZ = REMOVED
    #relative weight of OD split fractions (used to yield unique solution in OD estimation)
    relWeightODSplitFractions = 0.1
    
    #relevant platforms
    tracksConsidered = {"Utrecht":{5,7}, "Bijlmer": {2,3}, "AsdZ": {3,4}, "Schiphol": {3,4}}
    
    #upstream and downstream gate nodes
    upstreamNode = "up" #will be prefixed with a 'G' automatically
    downstreamNode = "down"  #will be prefixed with a 'G' automatically
    upstreamPlatform = "upP0"
    downstreamPlatform = "downP0"
    dwellTimeUpDownStream = 5*60 #dwell time at auxiliary up- and downstream stations
    # time between departure at downstream node and first arrival,
    # and between last real departure and arrival at downstream node
    timeDeltaUpDownTrip = 20*60
    
    nameLog = "/log_"
    nameGraph = "/pedGraph" 
    
    # POST-PROCESSING
    timeAnalysisStart = '07:00:00' 
    timeAnalysisEnd = '09:00:00'
    analysisPlotInterval = 900 #every 30 min
    numTimePointsAnalysis = 360
    exportTIKZ = True
    savePlots = True
    
    
    plotLinkFlows = {('G61021','AN200'), ('G61022','AN2122')} 
    plotAreaDensities = {'UA10','UA11','BA1617','UA27','BA7'} #set of areas to plot density 'UA10','UA11','BA1617','UA27','BA7'
    plotStations = set( stationNameDict.values() )
    plotConnections = [('Utrecht','Bijlmer'), ('Utrecht','AsdZ'), ('Utrecht','Schiphol'), ('Bijlmer','AsdZ'), ('Bijlmer','Schiphol'), ('AsdZ','Schiphol')]
    plotRidershipStations = {'Utrecht', 'Bijlmer', 'AsdZ', 'Schiphol'}
    plotMaxDensity =  1.75 #(crit dens = 1.75) for plotting time-density curve of individual areas
    plotAreasLOSDistribution = list(plotAreaDensities)
    aggregatedFlowValidation = {'asdzIn':{'asdzEscIn','asdzStairsIn'}, 'asdzOut':{'asdzEscOut','asdzStairsOut'},
        'utIn':{'utStairsNorthIn', 'utEscNorthIn', 'utEscSouthIn', 'utStairsSouthIn'},
        'utOut':{'utStairsNorthOut', 'utEscNorthOut', 'utEscSouthOut', 'utStairsSouthOut'},
        'shlIn':{'shlRampNorthIn', 'shlEscNorthIn', 'shlEscStairsSouthIn', 'shlRampSouthIn'},
        'shlOut':{'shlRampNorthOut', 'shlEscNorthOut', 'shlEscStairsSouthOut', 'shlRampSouthOut'}
        }
    
    #
    #heatmap
    #
    #plotHeatMapStations = {'AsdZ'}
    filenameAreaCoord = "data/areaCoordPlatforms_v3.csv"
    losLevelColors = {'A':(0,0,1),'B':(0,1,1),'C':(0,1,0),'D':(1,1,0),'E':(1,92/255,0),'F':(1,0,0)}
    peakPeriodDuration = 300 #duration of peak period in seconds
    
    #coordinates of platform center (rotation center heat map)
    platformCoordinateCenterDict = {'Utrecht': (268.98752805864314, -34.62698306337655),
                  'Bijlmer': (205.94864186294774, -22.0309402153114),
                  'AsdZ': (257.5976195542615, 151.3439354910965),
                  'Schiphol': (0,10)}
    
    #angles in radian (for alignment of heat map)
    platformAngleDict = {'Utrecht': 0+3.1415926536,
                  'Bijlmer': 0.015+3.1415926536,
                  'AsdZ': -0.002+3.1415926536,
                  'Schiphol': 0}
    
    #platform displacement (for heat map)    
    platformTranslationDict = {'Utrecht':[-265,135], 'Bijlmer':[-205,82], 'AsdZ':[-255,-125], 'Schiphol':[-12,-12]}
    
    #platform contour lines (for heat map)
    contourLines = dict()
    contourLines['Utrecht'] = [
        [(154.163523297285, -23.0493366658952), (154.015431536193, -23.0600027986882), (144.019237662449, -23.1339605293767), (140.856420764831, -23.1552046451048), (136.783897334788, -23.1868504440525), (134.033709921499, -23.2080064099229), (124.037427897898, -23.3032082563395), (122.196858867177, -23.3244523720677), (114.041234024155, -23.4302322014194), (111.269802495138, -23.4830339662375), (108.054095682844, -23.5360120307712), (104.045040150412, -23.6206358942526), (94.0595124094612, -23.8850854676321), (84.0632303858602, -24.234158904493), (74.0776144950521, -24.6572782219001), (64.1025765871791, -25.1543552699957), (54.116960696371, -25.7362324812883), (44.1525007714333, -26.3919792734115), (44.9881614233124, -38.5355918328537), (47.1778038908942, -38.5566596488663), (52.1706118362983, -38.5673257816593), (53.6938413789639, -38.5673257816593), (62.1668057100416, -38.5460816659311), (68.6828431981112, -38.5144358669834), (72.1629995837848, -38.493279901113), (82.1592816073859, -38.4403899864371), (92.1553873312714, -38.3980780546964), (102.151581205015, -38.3768339389683), (112.147775078758, -38.3556779730979), (122.143968952501, -38.3451881400205), (132.129584843309, -38.3556779730979), (139.904402300665, -38.3663441058909), (142.125778717053, -38.3663441058909), (152.121972590796, -38.3874119219034), (162.118166464539, -38.4086560376316), (165.534854952602, -38.4192340205668), (172.114360338282, -38.4297238536442), (180.058425522601, -38.4403899864371), (182.110554212026, -38.4508798195145), (192.106748085769, -38.4614578024497), (194.581996092601, -38.4720357853849), (202.102941959512, -38.4827019181778), (212.099135833256, -38.5037697341904), (222.084751724064, -38.5249257000608), (232.080945597807, -38.5460816659311), (242.07713947155, -38.5566596488663), (252.073333345294, -38.5779037645944), (260.990572959649, -38.598971580607), (262.069527219037, -38.598971580607), (272.06572109278, -38.6201275464774), (282.061914966523, -38.6412835123477), (292.058020690409, -38.6625276280759), (302.043636581217, -38.673105611011), (310.421487215736, -38.6941734270236), (310.67535880618, -38.6941734270236), (312.039918604818, -38.6941734270236), (322.036024328704, -38.715329392894), (332.032306352305, -38.7364853587643), (342.028500226048, -38.7577294744925), (348.290666123673, -38.7682193075699), (352.024605949933, -38.7788854403628), (360.349566669776, -38.8105312393106), (362.020887973534, -38.8211092222457), (372.01699369742, -38.8845771198568), (376.301164936025, -38.9163110686623), (382.002697738086, -38.9903569492086), (382.933560236381, -39.0009349321438), (387.006083666425, -39.0855587956252), (391.998891611829, -39.2125827407051), (396.991699557233, -39.3712524847328), (401.984507502637, -39.5615680277082), (405.506975820051, -39.7096597888007), (406.977315448041, -39.783705669347), (411.970123393445, -40.0270874267138), (416.962931338849, -40.3126048161059), (421.945161301318, -40.630032454019), (426.937969246722, -40.9685279079447), (431.920199209191, -41.3493352936111), (436.341796076096, -41.7089867134071), (438.235166871635, -41.867568307577), (438.943979878149, -41.9311243550459), (441.874081151194, -42.1849959454902), (449.870948100331, -42.8937208021471), (451.838541076131, -43.0629685291099), (461.792423018134, -43.9515190956649), (463.389698441346, -44.0995227068996), (463.632992048855, -44.1207668226278), (467.388175990843, -44.4486842936183), (471.746304960137, -44.8400696622199), (475.808250407245, -45.1785651161456), (476.728534922605, -45.252522846834), (481.710764885074, -45.6439082154356), (485.920713943417, -45.9719138362839), (488.237380356079, -46.141073413389), (490.141329134554, -46.2680092086111), (491.675224810012, -46.3738771878207), (493.494549725005, -46.5008129830428), (493.822555345853, -41.031907655698), (493.515793840733, -40.9790177410221), (492.42626159841, -40.8097700140592), (487.486343567682, -40.0059314608435), (482.567493352966, -39.1596928260292), (477.923846994281, -38.3345220072276), (473.290690468673, -37.467127406543), (472.730057373108, -37.361435727049), (462.913601059405, -35.4784666147295), (457.751633536896, -34.4841362188227), (456.767881123924, -34.2937325259895), (455.170605700713, -33.9763930379342), (453.107899028353, -33.5850958191904), (447.152494635848, -32.4425855123334), (443.280952881572, -31.7127928396639), (437.515864032043, -30.6338385802757), (436.045612553911, -30.3693890068963), (433.454006734792, -29.8932916249554), (428.535156520076, -29.036475007206), (427.868831745018, -28.9306951778542), (423.595238489348, -28.2325483041325), (420.220950082884, -27.7142271403088), (418.18997735933, -27.4075537850464), (416.835995543627, -27.2171500922132), (413.71549057775, -26.7728748089357), (408.754416581151, -26.1275297000321), (403.793342584553, -25.5458287884551), (398.821602455161, -25.0169296416961), (393.850038625485, -24.5514983925483), (388.867720513159, -24.1389570580764), (388.79376278247, -24.1389570580764), (387.30226718861, -24.0225992457894), (383.885578700548, -23.7898836212155), (383.060496031604, -23.747483539617), (380.373688366068, -23.5889019454471), (377.327229280737, -23.4302322014194), (376.872287864667, -23.4090762355491), (373.899962809739, -23.2715624573918), (368.907154864335, -23.0917367474937), (363.914258769074, -22.9648009522716), (358.709979314824, -22.8801770887902), (353.918153045188, -22.8377770071917), (343.921959171445, -22.7848870925158), (337.659793273819, -22.7743091095806), (333.925765297701, -22.7637311266454), (323.929571423958, -22.7637311266454), (313.933289400357, -22.7637311266454), (303.937183676472, -22.7637311266454), (293.951567785664, -22.7637311266454), (284.50542902455, -22.7637311266454), (283.955285762062, -22.7637311266454), (273.959180038177, -22.7637311266454), (269.516339055544, -22.7637311266454), (263.962898014576, -22.7637311266454), (254.53800336919, -22.7637311266454), (253.96679229069, -22.7637311266454), (243.970598416947, -22.7637311266454), (233.974404543204, -22.7531531437103), (223.978210669461, -22.7531531437103), (213.992594778652, -22.7531531437103), (203.996400904909, -22.7531531437103), (202.56837320866, -22.7531531437103), (194.000207031166, -22.7637311266454), (184.004013157423, -22.8272871741143), (182.840435034553, -22.8272871741143), (174.007819283679, -22.9013330546605), (154.163523297285, -23.0493366658952)],
        [(63.3409618158463, -34.6639619287208), (56.1479334199252, -34.5793380652393), (56.1796673687308, -27.968098730753), (63.3092278670408, -27.9469427648827)],
        [(236.195692809733, -29.8192457444092), (251.146173141025, -29.8192457444092), (251.146173141025, -26.3285995256582), (236.206358942526, -26.4026454062045)],
        [(220.942241417207, -25.6726764338194), (229.214224072516, -25.6198746690013), (229.214224072516, -30.517392618131), (220.942241417207, -30.475168836248)],
        [(197.067822082368, -30.4857468191832), (205.096511130168, -30.4963248021184), (205.118107845327, -25.6198746690013), (197.078400065303, -25.6516086178068)],
        [(293.517870485321, -25.6620984508842), (276.328648215657, -25.6410306348717), (276.328648215657, -30.5385485840013), (293.475470403723, -30.517392618131)],
        [(293.517870485321, -25.6620984508842), (276.328648215657, -25.6410306348717), (276.328648215657, -30.5385485840013), (293.475470403723, -30.517392618131)],
        [(305.7, -30.65), (299.34, -30.65), (299.26, -34.81), (305.7,-34.81)]
        ]
    
    contourLines['Bijlmer'] = [
            [(382.911292421988, -31.1557091201237), (391.924454681451, -18.715006283118), (374.704236927984, -18.4071623608758), (346.399522208007, -17.7354067229932), (329.180362337434, -17.1905970324271), (304.567658918575, -16.5812564853084), (275.286518287157, -15.857664585605), (250.188246619814, -15.4546112028755), (222.997482587538, -15.0526157030403), (196.04685797227, -14.6495623203108), (162.621990043866, -14.2475668204756), (130.898197809501, -13.7852719956651), (92.0664904083136, -13.1748735656521), (69.7567980503533, -13.0024386538807), (65.4342885442304, -12.9061713104991), (20.0997749917609, -13.0024386538807), (20.0997749917609, -15.0325159280485), (40.5380725096988, -15.1605197582592), (40.4111265623824, -25.1881917133593), (19.9728290444445, -25.0623036489372), (19.9728290444445, -27.0934388059994), (39.080309881349, -27.2320214651531), (75.1974897757547, -27.5959331807934), (116.259214318134, -28.0539964740267), (152.372162680962, -28.4559919738619), (173.498084080197, -28.6918998592915), (230.527493029188, -29.3266295958734), (305.893186185137, -30.2797820836406), (351.350414153346, -30.7738133952802), (382.911292421988, -31.1557091201237)],
            [(206.075587810264, -24.426516029461), (194.015722815208, -24.2995700821446), (194.015722815208, -23.5378943982463), (157.455289988089, -23.0301106089808), (157.455289988089, -19.2217321894892), (194.015722815208, -19.7305738616491), (194.142668762524, -18.9678402948565), (206.075587810264, -19.0947862421728)]
        ]
    
    contourLines['AsdZ'] = [
        [(306.25, 153.43), (328.62, 153.46), (328.62, 149.42), (306.25, 149.32)],
        [(364.80, 153.64), (338.57, 153.50), (338.57, 149.47), (364.74, 149.62)],
        [(47.0789002127898, 146.175663568149), (47.0789002127898, 147.48), (36.05, 147.53), (36.01, 153.51), (47.0965393661104, 153.51), (47.0965393661104, 154.907044461866), (364.83060813081, 156.071228581028), (479.185239108523, 156.512207414044), (479.149960801882, 147.428043453914), (364.760051517527, 147.057621234181), (47.0789002127898, 146.175663568149)]
        ]
    
    contourLines['Schiphol'] = [
        [(-196.256, 1.683), (130.762, 1.472), (148.072, 1.054), (155.493, 0.782), (167.665, 0.188), (181.153, -0.609), (193.722, -1.521), (207.064, -2.627), (232.690, -5.252), (234.062, 8.529), (208.682, 10.687), (190.671, 11.986), (167.148, 13.333), (146.089, 14.167), (123.284, 14.645), (89.188, 14.845), (-198.506, 14.342), (-196.256, 1.683)], 
        [(-132.963, 10.965), (-109.728, 10.970), (-109.728, 7.370), (-132.963, 7.310)],
        [(-97.357, 10.971), (-84.560, 10.971), (-84.562, 7.374), (-97.362, 7.374)],
        [(-41.462, 7.347), (-54.262, 7.345), (-54.263, 10.945), (-41.463, 10.947)],
        [(-4.564, 7.322), (-27.768, 7.322), (-27.764, 10.918), (-4.564, 10.922)]
    ]
    
    plotStationLOSEvolutionAreas = {'AA2', 'AA3', 'AA4', 'AA5', 'AA6', 'AA7', 'AA8', 'AA9', 'AA10', 'AA11', 'AA12', 'AA13', 'AA14', 'AA15', 'AA16', 'AA17', 'AA18', 'AA19', 'AA21',
        'BA1', 'BA2', 'BA3', 'BA4', 'BA5', 'BA6', 'BA7', 'BA8', 'BA9', 'BA10', 'BA11', 'BA12', 'BA13', 'BA14', 'BA15', 'BA1617', 'BA18',
        'UA1', 'UA2', 'UA3', 'UA4', 'UA5', 'UA6', 'UA7', 'UA8', 'UA9', 'UA10', 'UA11', 'UA12', 'UA13', 'UA14', 'UA15', 'UA16', 'UA17', 'UA18', 'UA19', 'UA20', 'UA21', 'UA22', 'UA23', 'UA24', 'UA25', 'UA26', 'UA27', 'UA28',
        'SA1', 'SA2', 'SA3', 'SA4', 'SA5', 'SA6', 'SA7', 'SA8', 'SA9', 'SA10', 'SA11', 'SA12', 'SA13', 'SA14', 'SA15', 'SA16', 'SA17', 'SA18', 'SA19', 'SA20', 'SA21', 'SA22', 'SA23', 'SA24', 'SA25', 'SA26', 'SA27', 'SA28'}
    
    gateIDLinkNameDict = {
        '74001': ('G74001', 'BN190'),
        '74002': ('G74002', 'BN190'),
        '74003': ('G74003', 'BN190'),
        '74004': ('G74004', 'BN190'),
        '74005': ('G74005', 'BN190'),
        '74006': ('G74006', 'BN190'),
        '61001': ('G61001', 'AN200'),
        '61002': ('G61002', 'AN2022'), #this gate is resampled to distinguish between stairs and escalators
        '61003': ('G61003', 'AN200'),
        '61004': ('G61004', 'AN12'),
        '61005': ('G61005', 'AN12'),
        '561001': ('G561001', 'G561001H'),
        '561002': ('G561002', 'G561002H'),
        '561003': ('G561003', 'G561003H'),
        '561004': ('G561004', 'G561004H'),
        '561005': ('G561005', 'G561005H')
    }
    
    gateIDStationNameDict = {
        '74001': 'Bijlmer',
        '74002': 'Bijlmer',
        '74003': 'Bijlmer',
        '74004': 'Bijlmer',
        '74005': 'Bijlmer',
        '74006': 'Bijlmer',
        '61001': 'AsdZ',
        '61002': 'AsdZ',
        '61003': 'AsdZ',
        '61004': 'AsdZ',
        '61005': 'AsdZ',
        '561001': 'Schiphol',
        '561002': 'Schiphol',
        '561003': 'Schiphol',
        '561004': 'Schiphol',
        '561005': 'Schiphol'
    }

    #comparison to link flow observations (ASE)
    asdzLinkFlowObsFile = "data/Asdz_flowObs_March2017.csv"
    utLinkFlowObsFile = "data/Ut_flowObs_March2017.csv"
    shlLinkFlowObsFile = "data/Shl_flowObs_March2017.csv"
    flowSensorLinkNameDict = {
        'asdzEscIn' : ('AN102', 'AN200'), 
        'asdzEscOut' : ('AN200', 'AN102'),
        'asdzStairsIn' : ('AN152', 'AN2122'),
        'asdzStairsOut' : ('AN2122', 'AN152'),
        'utStairsNorthIn': ('UN63', 'UN230'),
        'utStairsNorthOut': ('UN230', 'UN63'),
        'utEscNorthIn': ('UN83', 'UN250'),
        'utEscNorthOut': ('UN240', 'UN83'),
        'utEscSouthIn': ('UN123', 'UN260'),
        'utEscSouthOut': ('UN270', 'UN123'),
        'utStairsSouthIn': ('UN133', 'UN280'),
        'utStairsSouthOut': ('UN280', 'UN133'),
        'shlRampNorthIn': ('SN20', 'SN2122'),
        'shlRampNorthOut': ('SN2122', 'SN20'),
        'shlEscNorthIn': ('SN50', 'SN2324'),
        'shlEscNorthOut': ('SN2324', 'SN50'),
        'shlEscStairsSouthIn': ('SN104','SN2526'),
        'shlEscStairsSouthOut': ('SN2526','SN104'),
        'shlRampSouthIn': ('SN133','SN2728'),
        'shlRampSouthOut': ('SN2728','SN133')
    }
    
    utFloorFieldLayoutFile = "data/Ut_floorField.csv"
    utFloorFieldOccupancyFile="data/Ut_floorOccupancy_March2017.csv"
    
    
    def __init__(self, caseStudyDate):
        self.outputFolder =  Parameter.scenarioName + caseStudyDate
        
        self.fileNameLog = self.outputFolder + self.nameLog
        self.fileNameGraph = self.outputFolder + self.nameGraph
        self.outputDirectories = [self.outputFolder + '/', self.outputFolder + '/' + self.postProcessFolder, \
            self.outputFolder + '/' + self.postProcessFolder + '/heatmaps']
        
        
        #remove output directory if it exists
        if Parameter.postProcessOnly:
            shutil.rmtree(self.outputFolder + '/' + self.postProcessFolder, ignore_errors=True)
        else:
            shutil.rmtree(self.outputFolder, ignore_errors=True)
        
        #generate output directory
        for curDir in self.outputDirectories:
            if not os.path.exists(curDir):
                os.makedirs(curDir)
                
        #case study start and end date
        self.dateStart = datetime.datetime.strptime(caseStudyDate + ' ' + Parameter.timeCaseStudyStart, '%Y-%m-%d %H:%M:%S')
        self.dateEnd = datetime.datetime.strptime(caseStudyDate + ' ' + Parameter.timeCaseStudyEnd, '%Y-%m-%d %H:%M:%S')
        
        self.midnightCaseStudy = datetime.datetime.strptime(caseStudyDate, '%Y-%m-%d')
        self.dayCaseStudyString = caseStudyDate
        
        self.dateStartSec = (self.dateStart - self.midnightCaseStudy).total_seconds()
        
        #generate data points
        self.dateAnalysisStart = datetime.datetime.strptime(caseStudyDate + ' ' + self.timeAnalysisStart,"%Y-%m-%d %H:%M:%S")
        self.dateAnalysisEnd = datetime.datetime.strptime(caseStudyDate + ' ' + self.timeAnalysisEnd,"%Y-%m-%d %H:%M:%S")
        
        assert(self.dateStart <= self.dateAnalysisStart), \
            "simulation period (%s) must begin before analysis period (%s)" % \
            (self.dateStart, self.dateAnalysisStart)
            
        assert(self.dateAnalysisEnd <= self.dateEnd), \
            "analysis period (%s) must end before simulation period (%s)" % \
            (self.dateAnalysisEnd, self.dateEnd)
        
        self.analysisStart = (self.dateAnalysisStart - self.midnightCaseStudy).total_seconds()
        self.analysisEnd = (self.dateAnalysisEnd - self.midnightCaseStudy).total_seconds()
        
        self.timeStepAnalysis = (self.analysisEnd - self.analysisStart)/self.numTimePointsAnalysis
        self.timePointsAnalysis = [self.analysisStart + (i+0.5)*self.timeStepAnalysis \
                                   for i in range(0,self.numTimePointsAnalysis)] 
        self.datePointsAnalysis = [self.dateAnalysisStart + datetime.timedelta(seconds=(i+0.5)*self.timeStepAnalysis ) \
                                   for i in range(0,self.numTimePointsAnalysis)]
        
        