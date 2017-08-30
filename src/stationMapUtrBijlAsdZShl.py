from parameter import Parameter

class StationMapUtrBijlAsdZShl(object):
    
    def __init__(self):

        self.stationNames = self.getStationNames()
        self.nodes = self.getNodes()
        self.areas = self.getAreas()
        self.edges = self.getEdges()
        self.interfaces = self.getAreaInterfaces()
        self.pedPaths = self.getPedPaths()    
        self.setPlatformAttributes()
        
    
    def getStationNames(self):
        return {'Upstream', 'Utrecht' ,'Bijlmer', 'AsdZ', 'Schiphol', 'Downstream'};
    
    def getNodes(self):
        
        nodesUpDown={'Gup', 'upN0', 'upN0T', 'Gdown', 'downN0', 'downN0T'}
        
        nodesUtr={
            'UN10', 'UN11', 'UN20', 'UN21', 'UN22', 'UN30', 'UN31', 'UN32', 'UN40', 'UN41',
            'UN42', 'UN50', 'UN51', 'UN52', 'UN53', 'UN54', 'UN60', 'UN61', 'UN62', 'UN63',
            'UN70', 'UN72', 'UN80', 'UN81', 'UN82', 'UN83', 'UN90', 'UN92', 'UN100', 'UN101',
            'UN102', 'UN110', 'UN112', 'UN120', 'UN121', 'UN122', 'UN123', 'UN130', 'UN132',
            'UN133', 'UN140', 'UN141', 'UN142', 'UN150', 'UN152', 'UN160', 'UN161', 'UN162',
            'UN170', 'UN172', 'UN180', 'UN181', 'UN182', 'UN190', 'UN191', 'UN192', 'UN201',
            'UN202', 'UN210', 'UN220', 'UN230', 'UN240', 'UN250', 'UN260', 'UN270', 'UN280',
            'UN501', 'UN502', 'UN503', 'UN504', 'UN505', 'G621003', 'G621004', 
            'G621001', 'G621002', 'UN21T', 'UN31T',
            'UN41T', 'UN51T', 'UN61T', 'UN81T', 'UN101T', 'UN121T', 'UN141T', 'UN161T',
            'UN181T', 'UN191T', 'UN201T', 'UN22T', 'UN32T', 'UN42T', 'UN52T', 'UN72T',
            'UN92T', 'UN112T', 'UN132T', 'UN152T', 'UN172T', 'UN182T', 'UN192T', 'UN202T',
            'GTransUtrecht', 'GTransUtrechtH' 
        }
        
        nodesBijl={
            'BN10', 'BN11', 'BN12', 'BN21', 'BN22', 'BN23', 'BN24', 'BN30', 'BN31', 'BN40',
           'BN43', 'BN50', 'BN51', 'BN53', 'BN60', 'BN63', 'BN70', 'BN71', 'BN73', 'BN80',
           'BN83', 'BN90', 'BN91', 'BN100', 'BN103', 'BN110', 'BN111', 'BN112', 'BN113',
           'BN120', 'BN121', 'BN123', 'BN130', 'BN131', 'BN133', 'BN140', 'BN141',
           'BN143', 'BN151', 'BN153', 'BN160170', 'BN180', 'BN190', 'G74001',
           'G74002', 'G74003', 'G74004', 'G74005', 'G74006', 'BN11T', 'BN21T', 'BN31T',
           'BN51T', 'BN71T', 'BN91T', 'BN111T', 'BN121T', 'BN131T', 'BN141T', 'BN151T',
           'BN12T', 'BN22T', 'BN43T', 'BN63T', 'BN83T', 'BN103T', 'BN113T', 'BN123T',
           'BN133T', 'BN143T', 'BN153T', 'GTransBijlmer'
        }
        
        nodesAsdZ={
            'G61005', 'G61004', 'AN12', 'AN23', 'AN30', 'AN31', 'AN34', 'AN40', 'AN41', 'AN45',
            'AN50', 'AN51', 'AN56', 'AN60', 'AN61', 'AN67', 'AN70', 'AN71', 'AN78', 'AN80',
            'AN81', 'AN89', 'AN90', 'AN91', 'AN910', 'AN100', 'AN101', 'AN102', 'AN110', 'AN1011', 'AN1012',
            'AN120', 'AN1113', 'AN1114', 'AN130', 'AN1315', 'AN1415', 'AN140', 'AN150', 'AN151', 'AN152', 'AN1516',
            'AN160', 'AN161', 'AN1617', 'AN170', 'AN171', 'AN200', 'G61003', 'G61002', 'G61001', 'G61021', 'G61022',
            'AN2022', 'AN2122', 'AN30T', 'AN40T', 'AN50T', 'AN60T', 'AN70T', 'AN80T', 'AN90T',
            'AN100T', 'AN110T', 'AN130T', 'AN150T', 'AN160T', 'AN170T', 'AN31T', 'AN41T',
            'AN51T', 'AN61T', 'AN71T', 'AN81T', 'AN91T', 'AN101T', 'AN120T', 'AN140T', 'AN151T',
            'AN161T', 'AN171T', 'GTransAsdZ', 'AN201'
        }
        
        nodesShl = {
            'SN10', 'SN11', 'SN12', 'SN20', 'SN21', 'SN22', 'SN23', 'SN24', 'SN30', 'SN31', 'SN40', 'SN42', 'SN50',
            'SN51', 'SN52', 'SN53', 'SN54', 'SN60', 'SN61', 'SN62', 'SN70', 'SN72', 'SN80', 'SN81', 'SN82', 'SN90',
            'SN92', 'SN101', 'SN102', 'SN103', 'SN104', 'SN105', 'SN110', 'SN111', 'SN120', 'SN122', 'SN130', 'SN131',
            'SN132', 'SN133', 'SN140', 'SN141', 'SN142', 'SN150', 'SN151', 'SN152', 'SN160', 'SN161', 'SN162', 'SN170',
            'SN171', 'SN172', 'SN180', 'SN181', 'SN182', 'SN190', 'SN191', 'SN192', 'SN201', 'SN202', 'SN2122', 'SN2324',
            'SN2526', 'SN2728', 'SN11T', 'SN21T', 'SN31T', 'SN51T', 'SN61T', 'SN81T', 'SN101T', 'SN111T', 'SN131T', 'SN141T',
            'SN151T', 'SN161T', 'SN171T', 'SN181T', 'SN191T', 'SN201T', 'SN12T', 'SN22T', 'SN42T', 'SN52T', 'SN72T',
            'SN92T', 'SN102T', 'SN122T', 'SN132T', 'SN142T', 'SN152T', 'SN162T', 'SN172T', 'SN182T', 'SN192T', 'SN202T',
            'GTransSchipholH', 'GTransSchiphol', 'G561001H', 'G561002H', 'G561003H', 'G561004H', 'G561005H', 'G561001', 'G561002', 'G561003', 'G561004', 'G561005'
        }
    
        return nodesUpDown | nodesUtr | nodesBijl | nodesAsdZ | nodesShl
        
    def getEdges(self):
        
        edgesUpDown = {
            ('Gup','upN0', 1, 'upA0', 'bidirWalkway'),
            ('upN0','upN0T', 1, 'upA0', 'bidirWalkway'),
            ('Gdown','downN0', 1, 'downA0', 'bidirWalkway'),
            ('downN0','downN0T', 1, 'downA0', 'bidirWalkway')
            }
                
        edgesUtr={
        ('UN10', 'UN11', 15.2, 'UA1', 'bidirWalkway'),
        ('UN10', 'UN20', 30, 'UA2', 'bidirWalkway'),
        ('UN10', 'UN21', 16.7, 'UA2', 'bidirWalkway'),
        ('UN10', 'UN22', 16.3, 'UA2', 'bidirWalkway'),
        ('UN20', 'UN21', 16.8, 'UA2', 'bidirWalkway'),
        ('UN20', 'UN22', 16.8, 'UA2', 'bidirWalkway'),
        ('UN21', 'UN22', 14.5, 'UA2', 'bidirWalkway'),
        ('UN20', 'UN30', 29.7, 'UA3', 'bidirWalkway'),
        ('UN20', 'UN31', 16.7, 'UA3', 'bidirWalkway'),
        ('UN20', 'UN32', 16.5, 'UA3', 'bidirWalkway'),
        ('UN30', 'UN31', 16.5, 'UA3', 'bidirWalkway'),
        ('UN30', 'UN32', 16.7, 'UA3', 'bidirWalkway'),
        ('UN31', 'UN32', 15.2, 'UA3', 'bidirWalkway'),
        ('UN30', 'UN40', 30, 'UA4', 'bidirWalkway'),
        ('UN30', 'UN41', 17, 'UA4', 'bidirWalkway'),
        ('UN30', 'UN42', 17, 'UA4', 'bidirWalkway'),
        ('UN40', 'UN41', 16.7, 'UA4', 'bidirWalkway'),
        ('UN40', 'UN42', 16.7, 'UA4', 'bidirWalkway'),
        ('UN41', 'UN42', 15.2, 'UA4', 'bidirWalkway'),
        ('UN40', 'UN50', 30, 'UA5', 'bidirWalkway'),
        ('UN40', 'UN51', 17.1, 'UA5', 'bidirWalkway'),
        ('UN40', 'UN52', 17.1, 'UA5', 'bidirWalkway'),
        ('UN50', 'UN51', 16.8, 'UA5', 'bidirWalkway'),
        ('UN50', 'UN52', 16.8, 'UA5', 'bidirWalkway'),
        ('UN50', 'UN53', 4, 'UA5', 'bidirWalkway'),
        ('UN50', 'UN54', 4, 'UA5', 'bidirWalkway'),
        ('UN51', 'UN52', 15.9, 'UA5', 'bidirWalkway'),
        ('UN54', 'UN60', 30, 'UA6', 'bidirWalkway'),
        ('UN54', 'UN61', 15.7, 'UA6', 'bidirWalkway'),
        ('UN54', 'UN62', 15.7, 'UA6', 'bidirWalkway'),
        ('UN60', 'UN61', 15.3, 'UA6', 'bidirWalkway'),
        ('UN60', 'UN62', 15.3, 'UA6', 'bidirWalkway'),
        ('UN61', 'UN62', 8, 'UA6', 'bidirWalkway'),
        ('UN62', 'UN63', 8.5, 'UA6', 'bidirWalkway'),
        ('UN53', 'UN62', 15.7, 'UA7', 'bidirWalkway'),
        ('UN53', 'UN70', 30, 'UA7', 'bidirWalkway'),
        ('UN53', 'UN72', 15.7, 'UA7', 'bidirWalkway'),
        ('UN62', 'UN72', 8, 'UA7', 'bidirWalkway'),
        ('UN70', 'UN62', 15.3, 'UA7', 'bidirWalkway'),
        ('UN70', 'UN72', 15.3, 'UA7', 'bidirWalkway'),
        ('UN60', 'UN80', 30, 'UA8', 'bidirWalkway'),
        ('UN60', 'UN81', 15.7, 'UA8', 'bidirWalkway'),
        ('UN60', 'UN82', 15.7, 'UA8', 'bidirWalkway'),
        ('UN80', 'UN81', 15.3, 'UA8', 'bidirWalkway'),
        ('UN80', 'UN82', 15.3, 'UA8', 'bidirWalkway'),
        ('UN81', 'UN82', 8, 'UA8', 'bidirWalkway'),
        ('UN82', 'UN83', 8.5, 'UA8', 'bidirWalkway'),
        ('UN70', 'UN82', 15.7, 'UA9', 'bidirWalkway'),
        ('UN70', 'UN90', 30, 'UA9', 'bidirWalkway'),
        ('UN70', 'UN92', 15.7, 'UA9', 'bidirWalkway'),
        ('UN82', 'UN92', 8, 'UA9', 'bidirWalkway'),
        ('UN90', 'UN82', 15.3, 'UA9', 'bidirWalkway'),
        ('UN90', 'UN92', 15.3, 'UA9', 'bidirWalkway'),
        ('UN80', 'UN100', 30, 'UA10', 'bidirWalkway'),
        ('UN80', 'UN101', 15.7, 'UA10', 'bidirWalkway'),
        ('UN80', 'UN102', 15.7, 'UA10', 'bidirWalkway'),
        ('UN100', 'UN101', 15.3, 'UA10', 'bidirWalkway'),
        ('UN100', 'UN102', 15.3, 'UA10', 'bidirWalkway'),
        ('UN101', 'UN102', 8, 'UA10', 'bidirWalkway'),
        ('UN90', 'UN102', 15.7, 'UA11', 'bidirWalkway'),
        ('UN90', 'UN110', 30, 'UA11', 'bidirWalkway'),
        ('UN90', 'UN112', 15.7, 'UA11', 'bidirWalkway'),
        ('UN102', 'UN112', 8, 'UA11', 'bidirWalkway'),
        ('UN110', 'UN102', 15.3, 'UA11', 'bidirWalkway'),
        ('UN110', 'UN112', 15.3, 'UA11', 'bidirWalkway'),
        ('UN100', 'UN120', 30, 'UA12', 'bidirWalkway'),
        ('UN100', 'UN121', 15.7, 'UA12', 'bidirWalkway'),
        #('UN100', 'UN122', 15.7, 'UA12', 'bidirWalkway'),
        ('UN100', 'UN123', 4.4, 'UA12', 'bidirWalkway'),
        ('UN120', 'UN121', 15.3, 'UA12', 'bidirWalkway'),
        ('UN120', 'UN122', 15.3, 'UA12', 'bidirWalkway'),
        ('UN121', 'UN122', 8, 'UA12', 'bidirWalkway'),
        ('UN121', 'UN123', 12.7, 'UA12', 'bidirWalkway'),
        #('UN122', 'UN123', 11.4, 'UA12', 'bidirWalkway'),
        ('UN110', 'UN122', 15.7, 'UA13', 'bidirWalkway'),
        ('UN110', 'UN130', 30, 'UA13', 'bidirWalkway'),
        ('UN110', 'UN132', 15.7, 'UA13', 'bidirWalkway'),
        ('UN122', 'UN132', 8, 'UA13', 'bidirWalkway'),
        ('UN122', 'UN133', 2, 'UA13', 'bidirWalkway'),
        ('UN130', 'UN122', 15.3, 'UA13', 'bidirWalkway'),
        ('UN130', 'UN132', 15.3, 'UA13', 'bidirWalkway'),
        ('UN120', 'UN140', 30, 'UA14', 'bidirWalkway'),
        ('UN120', 'UN141', 15.7, 'UA14', 'bidirWalkway'),
        ('UN120', 'UN142', 15.7, 'UA14', 'bidirWalkway'),
        ('UN140', 'UN141', 15.3, 'UA14', 'bidirWalkway'),
        ('UN140', 'UN142', 15.3, 'UA14', 'bidirWalkway'),
        ('UN141', 'UN142', 8, 'UA14', 'bidirWalkway'),
        ('UN130', 'UN142', 15.7, 'UA15', 'bidirWalkway'),
        ('UN130', 'UN150', 30, 'UA15', 'bidirWalkway'),
        ('UN130', 'UN152', 15.7, 'UA15', 'bidirWalkway'),
        ('UN142', 'UN152', 8, 'UA15', 'bidirWalkway'),
        ('UN150', 'UN142', 15.3, 'UA15', 'bidirWalkway'),
        ('UN150', 'UN152', 15.3, 'UA15', 'bidirWalkway'),
        ('UN140', 'UN160', 30, 'UA16', 'bidirWalkway'),
        ('UN140', 'UN161', 15.6, 'UA16', 'bidirWalkway'),
        ('UN140', 'UN162', 15.8, 'UA16', 'bidirWalkway'),
        ('UN160', 'UN161', 15.4, 'UA16', 'bidirWalkway'),
        ('UN160', 'UN162', 15.3, 'UA16', 'bidirWalkway'),
        ('UN161', 'UN162', 8, 'UA16', 'bidirWalkway'),
        ('UN150', 'UN162', 15.6, 'UA17', 'bidirWalkway'),
        ('UN150', 'UN170', 30, 'UA17', 'bidirWalkway'),
        ('UN150', 'UN172', 15.8, 'UA17', 'bidirWalkway'),
        ('UN162', 'UN172', 8, 'UA17', 'bidirWalkway'),
        ('UN170', 'UN162', 15.3, 'UA17', 'bidirWalkway'),
        ('UN170', 'UN172', 15.3, 'UA17', 'bidirWalkway'),
        ('UN160', 'UN180', 30.5, 'UA18', 'bidirWalkway'),
        ('UN160', 'UN181', 15.5, 'UA18', 'bidirWalkway'),
        ('UN170', 'UN180', 30.1, 'UA18', 'bidirWalkway'),
        ('UN170', 'UN182', 15.8, 'UA18', 'bidirWalkway'),
        ('UN180', 'UN181', 17, 'UA18', 'bidirWalkway'),
        ('UN180', 'UN182', 16.2, 'UA18', 'bidirWalkway'),
        ('UN181', 'UN182', 12.7, 'UA18', 'bidirWalkway'),
        ('UN180', 'UN190', 30.2, 'UA19', 'bidirWalkway'),
        ('UN180', 'UN191', 15.9, 'UA19', 'bidirWalkway'),
        ('UN180', 'UN192', 17.1, 'UA19', 'bidirWalkway'),
        ('UN190', 'UN191', 17, 'UA19', 'bidirWalkway'),
        ('UN190', 'UN192', 15.4, 'UA19', 'bidirWalkway'),
        ('UN191', 'UN192', 12.7, 'UA19', 'bidirWalkway'),
        ('UN190', 'UN201', 27.8, 'UA20', 'bidirWalkway'),
        ('UN190', 'UN202', 29, 'UA20', 'bidirWalkway'),
        ('UN201', 'UN202', 8.4, 'UA20', 'bidirWalkway'),
        ('UN11', 'UN210', 5.9, 'UA21', 'stairwayDown'),
        ('UN210', 'UN11', 5.9, 'UA21', 'stairwayUp'),
        ('UN50', 'UN220', 11.1, 'UA22', 'stairwayDown'),
        ('UN220', 'UN50', 11.1, 'UA22', 'stairwayUp'),
        ('UN63', 'UN230', 11.9, 'UA23', 'stairwayUp'),
        ('UN230', 'UN63', 11.9, 'UA23', 'stairwayDown'),
        ('UN240', 'UN83', 13.5, 'UA24', 'escalatorDown'),
        ('UN83', 'UN250', 13.5, 'UA25', 'escalatorUp'),
        ('UN123', 'UN260', 13.4, 'UA26', 'escalatorUp'),
        ('UN270', 'UN123', 13.4, 'UA27', 'escalatorDown'),
        ('UN133', 'UN280', 11.5, 'UA28', 'stairwayUp'),
        ('UN280', 'UN133', 11.5, 'UA28', 'stairwayDown'),
        ('UN280', 'GTransUtrechtH', 100, 'UA50', 'bidirWalkway'),
        ('UN220', 'UN501', 134.7, 'UA50', 'bidirWalkway'),
        ('UN220', 'UN502', 68.2, 'UA50', 'bidirWalkway'),
        ('UN220', 'UN505', 86.5, 'UA50', 'bidirWalkway'),
        ('UN220', 'GTransUtrechtH', 100, 'UA50', 'bidirWalkway'),
        ('UN230', 'UN502', 26.1, 'UA50', 'bidirWalkway'),
        ('UN230', 'UN505', 39.1, 'UA50', 'bidirWalkway'),
        ('UN230', 'GTransUtrechtH', 100, 'UA50', 'bidirWalkway'),
        ('UN240', 'UN503', 4.8, 'UA50', 'bidirWalkway'),
        ('UN250', 'UN503', 4.8, 'UA50', 'bidirWalkway'),
        ('UN260', 'UN504', 5, 'UA50', 'bidirWalkway'),
        ('UN270', 'UN504', 5, 'UA50', 'bidirWalkway'),
        ('UN280', 'UN502', 40.9, 'UA50', 'bidirWalkway'),
        ('UN280', 'UN501', 85.6, 'UA50', 'bidirWalkway'),
        ('UN280', 'UN504', 27.1, 'UA50', 'bidirWalkway'),
        ('UN501', 'UN502', 66.5, 'UA50', 'bidirWalkway'),
        ('UN502', 'UN503', 15.8, 'UA50', 'bidirWalkway'),
        ('UN502', 'UN504', 24.4, 'UA50', 'bidirWalkway'),
        ('UN503', 'UN505', 35, 'UA50', 'bidirWalkway'),
        ('UN503', 'GTransUtrechtH', 100, 'UA50', 'bidirWalkway'),
        ('UN504', 'UN505', 40, 'UA50', 'bidirWalkway'),
        ('UN504', 'GTransUtrechtH', 100, 'UA50', 'bidirWalkway'),
        ('UN21', 'UN21T', 0.111, 'UA2', 'bidirWalkway'),
        ('UN31', 'UN31T', 0.111, 'UA3', 'bidirWalkway'),
        ('UN41', 'UN41T', 0.111, 'UA4', 'bidirWalkway'),
        ('UN51', 'UN51T', 0.111, 'UA5', 'bidirWalkway'),
        ('UN61', 'UN61T', 0.111, 'UA6', 'bidirWalkway'),
        ('UN81', 'UN81T', 0.111, 'UA8', 'bidirWalkway'),
        ('UN101', 'UN101T', 0.111, 'UA10', 'bidirWalkway'),
        ('UN121', 'UN121T', 0.111, 'UA12', 'bidirWalkway'),
        ('UN141', 'UN141T', 0.111, 'UA14', 'bidirWalkway'),
        ('UN161', 'UN161T', 0.111, 'UA16', 'bidirWalkway'),
        ('UN181', 'UN181T', 0.111, 'UA18', 'bidirWalkway'),
        ('UN191', 'UN191T', 0.111, 'UA19', 'bidirWalkway'),
        ('UN201', 'UN201T', 0.111, 'UA20', 'bidirWalkway'),
        ('UN22', 'UN22T', 0.111, 'UA2', 'bidirWalkway'),
        ('UN32', 'UN32T', 0.111, 'UA3', 'bidirWalkway'),
        ('UN42', 'UN42T', 0.111, 'UA4', 'bidirWalkway'),
        ('UN52', 'UN52T', 0.111, 'UA5', 'bidirWalkway'),
        ('UN72', 'UN72T', 0.111, 'UA7', 'bidirWalkway'),
        ('UN92', 'UN92T', 0.111, 'UA9', 'bidirWalkway'),
        ('UN112', 'UN112T', 0.111, 'UA11', 'bidirWalkway'),
        ('UN132', 'UN132T', 0.111, 'UA13', 'bidirWalkway'),
        ('UN152', 'UN152T', 0.111, 'UA15', 'bidirWalkway'),
        ('UN172', 'UN172T', 0.111, 'UA17', 'bidirWalkway'),
        ('UN182', 'UN182T', 0.111, 'UA18', 'bidirWalkway'),
        ('UN192', 'UN192T', 0.111, 'UA19', 'bidirWalkway'),
        ('UN202', 'UN202T', 0.111, 'UA20', 'bidirWalkway'),
        ('G621003', 'UN210', 86.3, 'UA50', 'bidirWalkway'),
        ('G621004', 'UN210', 60.1, 'UA50', 'bidirWalkway'),
        ('G621001', 'UN501', 60, 'UA50', 'bidirWalkway'),
        ('G621002', 'UN505', 1, 'UA50', 'bidirWalkway'),
        ('GTransUtrecht', 'GTransUtrechtH', 1, 'UA50', 'bidirWalkway'),
        }
        
        edgesBijl = {('BN10', 'BN11', 23, 'BA1', 'bidirWalkway'),
        ('BN10', 'BN12', 23.2, 'BA1', 'bidirWalkway'),
        ('BN10', 'BN21', 17, 'BA2', 'bidirWalkway'),
        ('BN10', 'BN22', 16.9, 'BA2', 'bidirWalkway'),
        ('BN10', 'BN23', 31, 'BA2', 'bidirWalkway'),
        ('BN10', 'BN24', 31.1, 'BA2', 'bidirWalkway'),
        ('BN21', 'BN22', 15.1, 'BA2', 'bidirWalkway'),
        ('BN21', 'BN23', 19.6, 'BA2', 'bidirWalkway'),
        ('BN21', 'BN24', 15.8, 'BA2', 'bidirWalkway'),
        ('BN22', 'BN23', 15.8, 'BA2', 'bidirWalkway'),
        ('BN22', 'BN24', 19.8, 'BA2', 'bidirWalkway'),
        ('BN24', 'BN30', 29.1, 'BA3', 'bidirWalkway'),
        ('BN24', 'BN31', 14.8, 'BA3', 'bidirWalkway'),
        ('BN30', 'BN31', 14.8, 'BA3', 'bidirWalkway'),
        ('BN23', 'BN40', 29.2, 'BA4', 'bidirWalkway'),
        ('BN23', 'BN43', 14.8, 'BA4', 'bidirWalkway'),
        ('BN40', 'BN43', 15, 'BA4', 'bidirWalkway'),
        ('BN30', 'BN50', 29.3, 'BA5', 'bidirWalkway'),
        ('BN30', 'BN51', 15.1, 'BA5', 'bidirWalkway'),
        ('BN30', 'BN53', 25.9, 'BA5', 'bidirWalkway'),
        ('BN50', 'BN51', 14.9, 'BA5', 'bidirWalkway'),
        ('BN50', 'BN53', 5.5, 'BA5', 'bidirWalkway'),
        ('BN51', 'BN53', 12.9, 'BA5', 'bidirWalkway'),
        ('BN40', 'BN53', 25.9, 'BA6', 'bidirWalkway'),
        ('BN40', 'BN60', 29.4, 'BA6', 'bidirWalkway'),
        ('BN40', 'BN63', 15.1, 'BA6', 'bidirWalkway'),
        ('BN53', 'BN60', 5.5, 'BA6', 'bidirWalkway'),
        ('BN53', 'BN63', 12.9, 'BA6', 'bidirWalkway'),
        ('BN60', 'BN63', 15, 'BA6', 'bidirWalkway'),
        ('BN50', 'BN70', 28.8, 'BA7', 'bidirWalkway'),
        ('BN50', 'BN71', 14.9, 'BA7', 'bidirWalkway'),
        ('BN50', 'BN73', 5.5, 'BA7', 'bidirWalkway'),
        ('BN70', 'BN71', 14.9, 'BA7', 'bidirWalkway'),
        ('BN70', 'BN73', 25.3, 'BA7', 'bidirWalkway'),
        ('BN71', 'BN73', 12.9, 'BA7', 'bidirWalkway'),
        ('BN60', 'BN73', 5.5, 'BA8', 'bidirWalkway'),
        ('BN60', 'BN80', 28.8, 'BA8', 'bidirWalkway'),
        ('BN60', 'BN83', 14.6, 'BA8', 'bidirWalkway'),
        ('BN73', 'BN80', 25.2, 'BA8', 'bidirWalkway'),
        ('BN73', 'BN83', 12.5, 'BA8', 'bidirWalkway'),
        ('BN80', 'BN83', 14.9, 'BA8', 'bidirWalkway'),
        ('BN70', 'BN90', 29.1, 'BA9', 'bidirWalkway'),
        ('BN70', 'BN91', 14.9, 'BA9', 'bidirWalkway'),
        ('BN90', 'BN91', 14.7, 'BA9', 'bidirWalkway'),
        ('BN80', 'BN100', 29.1, 'BA10', 'bidirWalkway'),
        ('BN80', 'BN103', 14.7, 'BA10', 'bidirWalkway'),
        ('BN100', 'BN103', 14.8, 'BA10', 'bidirWalkway'),
        ('BN110', 'BN111', 17.1, 'BA11', 'bidirWalkway'),
        ('BN110', 'BN112', 30.5, 'BA11', 'bidirWalkway'),
        ('BN110', 'BN113', 17.1, 'BA11', 'bidirWalkway'),
        ('BN90', 'BN110', 30.9, 'BA11', 'bidirWalkway'),
        ('BN90', 'BN111', 15.4, 'BA11', 'bidirWalkway'),
        ('BN90', 'BN112', 5.0, 'BA11', 'bidirWalkway'),
        ('BN90', 'BN113', 19.3, 'BA11', 'bidirWalkway'),
        ('BN100', 'BN110', 31.1, 'BA11', 'bidirWalkway'),
        ('BN100', 'BN111', 19.8, 'BA11', 'bidirWalkway'),
        ('BN100', 'BN112', 5, 'BA11', 'bidirWalkway'),
        ('BN100', 'BN113', 15.4, 'BA11', 'bidirWalkway'),
        ('BN111', 'BN112', 17, 'BA11', 'bidirWalkway'),
        ('BN111', 'BN113', 14.6, 'BA11', 'bidirWalkway'),
        ('BN112', 'BN113', 16.6, 'BA11', 'bidirWalkway'),
        ('BN110', 'BN120', 30.8, 'BA12', 'bidirWalkway'),
        ('BN110', 'BN121', 17.2, 'BA12', 'bidirWalkway'),
        ('BN110', 'BN123', 17, 'BA12', 'bidirWalkway'),
        ('BN120', 'BN121', 16.7, 'BA12', 'bidirWalkway'),
        ('BN120', 'BN123', 16.9, 'BA12', 'bidirWalkway'),
        ('BN121', 'BN123', 14.6, 'BA12', 'bidirWalkway'),
        ('BN120', 'BN130', 30.9, 'BA13', 'bidirWalkway'),
        ('BN120', 'BN131', 17.2, 'BA13', 'bidirWalkway'),
        ('BN120', 'BN133', 16.9, 'BA13', 'bidirWalkway'),
        ('BN130', 'BN131', 16.9, 'BA13', 'bidirWalkway'),
        ('BN130', 'BN133', 17.2, 'BA13', 'bidirWalkway'),
        ('BN131', 'BN133', 14.2, 'BA13', 'bidirWalkway'),
        ('BN130', 'BN140', 30.7, 'BA14', 'bidirWalkway'),
        ('BN130', 'BN141', 16.9, 'BA14', 'bidirWalkway'),
        ('BN130', 'BN143', 16.6, 'BA14', 'bidirWalkway'),
        ('BN140', 'BN141', 16.3, 'BA14', 'bidirWalkway'),
        ('BN140', 'BN143', 17.2, 'BA14', 'bidirWalkway'),
        ('BN141', 'BN143', 14.2, 'BA14', 'bidirWalkway'),
        ('BN140', 'BN151', 29.9, 'BA15', 'bidirWalkway'),
        ('BN140', 'BN153', 34.2, 'BA15', 'bidirWalkway'),
        ('BN151', 'BN153', 14.1, 'BA15', 'bidirWalkway'),
        ('BN112', 'BN160170', 24.1, 'BA1617', 'escalatorDown'),
        #('BN112', 'BN170', 24.1, 'BA17', 'escalatorDown'),
        ('BN180', 'BN112', 24.1, 'BA18', 'escalatorUp'),
        ('BN160170', 'BN190', 1, 'BA19', 'bidirWalkway'),
        #('BN170', 'BN190', 1, 'BA19', 'bidirWalkway'),
        ('BN180', 'BN190', 1, 'BA19', 'bidirWalkway'),
        ('BN190', 'G74001', 21.9, 'BA19', 'bidirWalkway'),
        ('BN190', 'G74002', 4.5, 'BA19', 'bidirWalkway'),
        ('BN190', 'G74003', 50.6, 'BA19', 'bidirWalkway'),
        ('BN190', 'G74004', 71.2, 'BA19', 'bidirWalkway'),
        ('BN190', 'G74005', 16.8, 'BA19', 'bidirWalkway'),
        ('BN190', 'G74006', 60, 'BA19', 'bidirWalkway'),
        ('BN190', 'GTransBijlmer', 100, 'BA19', 'bidirWalkway'),
        ('BN11', 'BN11T', 0.111, 'BA1', 'bidirWalkway'),
        ('BN21', 'BN21T', 0.111, 'BA2', 'bidirWalkway'),
        ('BN31', 'BN31T', 0.111, 'BA3', 'bidirWalkway'),
        ('BN51', 'BN51T', 0.111, 'BA5', 'bidirWalkway'),
        ('BN71', 'BN71T', 0.111, 'BA7', 'bidirWalkway'),
        ('BN91', 'BN91T', 0.111, 'BA9', 'bidirWalkway'),
        ('BN111', 'BN111T', 0.111, 'BA11', 'bidirWalkway'),
        ('BN121', 'BN121T', 0.111, 'BA12', 'bidirWalkway'),
        ('BN131', 'BN131T', 0.111, 'BA13', 'bidirWalkway'),
        ('BN141', 'BN141T', 0.111, 'BA14', 'bidirWalkway'),
        ('BN151', 'BN151T', 0.111, 'BA15', 'bidirWalkway'),
        ('BN12', 'BN12T', 0.111, 'BA1', 'bidirWalkway'),
        ('BN22', 'BN22T', 0.111, 'BA2', 'bidirWalkway'),
        ('BN43', 'BN43T', 0.111, 'BA4', 'bidirWalkway'),
        ('BN63', 'BN63T', 0.111, 'BA6', 'bidirWalkway'),
        ('BN83', 'BN83T', 0.111, 'BA8', 'bidirWalkway'),
        ('BN103', 'BN103T', 0.111, 'BA10', 'bidirWalkway'),
        ('BN113', 'BN113T', 0.111, 'BA11', 'bidirWalkway'),
        ('BN123', 'BN123T', 0.111, 'BA12', 'bidirWalkway'),
        ('BN133', 'BN133T', 0.111, 'BA13', 'bidirWalkway'),
        ('BN143', 'BN143T', 0.111, 'BA14', 'bidirWalkway'),
        ('BN153', 'BN153T', 0.111, 'BA15', 'bidirWalkway')}
        
        edgesAsdZ={
        ('G61005', 'AN12', 11.2, 'AA1', 'bidirWalkway'),
        ('G61004', 'AN12', 27.5, 'AA1', 'bidirWalkway'),
        ('AN12', 'AN23', 10.8, 'AA2', 'stairwayUp'),
        ('AN23', 'AN12', 10.8, 'AA2', 'stairwayDown'),
        ('AN23', 'AN34', 46.5, 'AA3', 'bidirWalkway'),
        ('AN30', 'AN31', 8.8, 'AA3', 'bidirWalkway'),
        ('AN23', 'AN30', 23.7, 'AA3', 'bidirWalkway'),
        ('AN30', 'AN34', 23.7, 'AA3', 'bidirWalkway'),
        ('AN31', 'AN34', 23.7, 'AA3', 'bidirWalkway'),
        ('AN23', 'AN31', 23.7, 'AA3', 'bidirWalkway'),
        ('AN30', 'AN30T', 0.111, 'AA3', 'bidirWalkway'),
        ('AN31', 'AN31T', 0.111, 'AA3', 'bidirWalkway'),
        ('AN34', 'AN45', 30, 'AA4', 'bidirWalkway'),
        ('AN40', 'AN41', 8.8, 'AA4', 'bidirWalkway'),
        ('AN34', 'AN40', 15.6, 'AA4', 'bidirWalkway'),
        ('AN45', 'AN40', 15.6, 'AA4', 'bidirWalkway'),
        ('AN45', 'AN41', 15.6, 'AA4', 'bidirWalkway'),
        ('AN34', 'AN41', 15.6, 'AA4', 'bidirWalkway'),
        ('AN40', 'AN40T', 0.111, 'AA4', 'bidirWalkway'),
        ('AN41', 'AN41T', 0.111, 'AA4', 'bidirWalkway'),
        ('AN45', 'AN56', 30, 'AA5', 'bidirWalkway'),
        ('AN50', 'AN51', 8.8, 'AA5', 'bidirWalkway'),
        ('AN45', 'AN50', 15.6, 'AA5', 'bidirWalkway'),
        ('AN56', 'AN50', 15.6, 'AA5', 'bidirWalkway'),
        ('AN56', 'AN51', 15.6, 'AA5', 'bidirWalkway'),
        ('AN45', 'AN51', 15.6, 'AA5', 'bidirWalkway'),
        ('AN50', 'AN50T', 0.111, 'AA5', 'bidirWalkway'),
        ('AN51', 'AN51T', 0.111, 'AA5', 'bidirWalkway'),
        ('AN56', 'AN67', 30, 'AA6', 'bidirWalkway'),
        ('AN60', 'AN61', 8.8, 'AA6', 'bidirWalkway'),
        ('AN56', 'AN60', 15.6, 'AA6', 'bidirWalkway'),
        ('AN67', 'AN60', 15.6, 'AA6', 'bidirWalkway'),
        ('AN67', 'AN61', 15.6, 'AA6', 'bidirWalkway'),
        ('AN56', 'AN61', 15.6, 'AA6', 'bidirWalkway'),
        ('AN60', 'AN60T', 0.111, 'AA6', 'bidirWalkway'),
        ('AN61', 'AN61T', 0.111, 'AA6', 'bidirWalkway'),
        ('AN67', 'AN78', 30, 'AA7', 'bidirWalkway'),
        ('AN70', 'AN71', 8.9, 'AA7', 'bidirWalkway'),
        ('AN67', 'AN70', 15.6, 'AA7', 'bidirWalkway'),
        ('AN78', 'AN70', 15.6, 'AA7', 'bidirWalkway'),
        ('AN78', 'AN71', 15.6, 'AA7', 'bidirWalkway'),
        ('AN67', 'AN71', 15.6, 'AA7', 'bidirWalkway'),
        ('AN70', 'AN70T', 0.111, 'AA7', 'bidirWalkway'),
        ('AN71', 'AN71T', 0.111, 'AA7', 'bidirWalkway'),
        ('AN78', 'AN89', 30, 'AA8', 'bidirWalkway'),
        ('AN80', 'AN81', 8.9, 'AA8', 'bidirWalkway'),
        ('AN78', 'AN80', 15.6, 'AA8', 'bidirWalkway'),
        ('AN89', 'AN80', 15.6, 'AA8', 'bidirWalkway'),
        ('AN89', 'AN81', 15.6, 'AA8', 'bidirWalkway'),
        ('AN78', 'AN81', 15.6, 'AA8', 'bidirWalkway'),
        ('AN80', 'AN80T', 0.111, 'AA8', 'bidirWalkway'),
        ('AN81', 'AN81T', 0.111, 'AA8', 'bidirWalkway'),
        ('AN89', 'AN910', 30, 'AA9', 'bidirWalkway'),
        ('AN90', 'AN91', 8.9, 'AA9', 'bidirWalkway'),
        ('AN89', 'AN90', 15.6, 'AA9', 'bidirWalkway'),
        ('AN910', 'AN90', 15.6, 'AA9', 'bidirWalkway'),
        ('AN910', 'AN91', 15.6, 'AA9', 'bidirWalkway'),
        ('AN89', 'AN91', 15.6, 'AA9', 'bidirWalkway'),
        ('AN90', 'AN90T', 0.111, 'AA9', 'bidirWalkway'),
        ('AN91', 'AN91T', 0.111, 'AA9', 'bidirWalkway'),
        ('AN910', 'AN102', 32.7, 'AA10', 'bidirWalkway'),
        ('AN100', 'AN101', 8.9, 'AA10', 'bidirWalkway'),
        ('AN910', 'AN100', 16.9, 'AA10', 'bidirWalkway'),
        ('AN102', 'AN100', 16.9, 'AA10', 'bidirWalkway'),
        ('AN102', 'AN101', 16.9, 'AA10', 'bidirWalkway'),
        ('AN910', 'AN101', 16.9, 'AA10', 'bidirWalkway'),
        ('AN100', 'AN100T', 0.111, 'AA10', 'bidirWalkway'),
        ('AN101', 'AN101T', 0.111, 'AA10', 'bidirWalkway'),
        ('AN102', 'AN1011', 2, 'AA10', 'bidirWalkway'),
        ('AN1011', 'AN1113', 27.3, 'AA11', 'bidirWalkway'),
        ('AN1011', 'AN110', 13.7, 'AA11', 'bidirWalkway'),
        ('AN1113', 'AN110', 13.7, 'AA11', 'bidirWalkway'),
        ('AN110', 'AN110T', 0.111, 'AA11', 'bidirWalkway'),
        ('AN102', 'AN1012', 2, 'AA10', 'bidirWalkway'),
        ('AN1012', 'AN1114', 27.3, 'AA12', 'bidirWalkway'),
        ('AN1012', 'AN120', 13.7, 'AA12', 'bidirWalkway'),
        ('AN1114', 'AN120', 13.7, 'AA12', 'bidirWalkway'),
        ('AN120', 'AN120T', 0.111, 'AA12', 'bidirWalkway'),
        ('AN1315', 'AN152', 3.1, 'AA15', 'bidirWalkway'),
        ('AN1113', 'AN1315', 31.2, 'AA13', 'bidirWalkway'),
        ('AN1315', 'AN130', 16.1, 'AA13', 'bidirWalkway'),
        ('AN1415', 'AN152', 3.1, 'AA15', 'bidirWalkway'),
        ('AN1114', 'AN1415', 31.2, 'AA14', 'bidirWalkway'),
        ('AN1415', 'AN140', 16.1, 'AA14', 'bidirWalkway'),
        ('AN1113', 'AN130', 15.6, 'AA13', 'bidirWalkway'),
        ('AN130', 'AN130T', 0.111, 'AA13', 'bidirWalkway'),
        ('AN1114', 'AN140', 15.6, 'AA14', 'bidirWalkway'),
        ('AN140', 'AN140T', 0.111, 'AA14', 'bidirWalkway'),
        ('AN152', 'AN1516', 28.8, 'AA15', 'bidirWalkway'),
        ('AN150', 'AN151', 9, 'AA15', 'bidirWalkway'),
        ('AN152', 'AN150', 15.1, 'AA15', 'bidirWalkway'),
        ('AN1516', 'AN150', 15.1, 'AA15', 'bidirWalkway'),
        ('AN1516', 'AN151', 15.1, 'AA15', 'bidirWalkway'),
        ('AN152', 'AN151', 15.1, 'AA15', 'bidirWalkway'),
        ('AN150', 'AN150T', 0.111, 'AA15', 'bidirWalkway'),
        ('AN151', 'AN151T', 0.111, 'AA15', 'bidirWalkway'),
        ('AN1516', 'AN1617', 30, 'AA16', 'bidirWalkway'),
        ('AN160', 'AN161', 9, 'AA16', 'bidirWalkway'),
        ('AN1516', 'AN160', 15.7, 'AA16', 'bidirWalkway'),
        ('AN1617', 'AN160', 15.7, 'AA16', 'bidirWalkway'),
        ('AN1617', 'AN161', 15.7, 'AA16', 'bidirWalkway'),
        ('AN1516', 'AN161', 15.7, 'AA16', 'bidirWalkway'),
        ('AN160', 'AN160T', 0.111, 'AA16', 'bidirWalkway'),
        ('AN161', 'AN161T', 0.111, 'AA16', 'bidirWalkway'),
        ('AN170', 'AN171', 9.1, 'AA17', 'bidirWalkway'),
        ('AN1617', 'AN170', 28.2, 'AA17', 'bidirWalkway'),
        ('AN1617', 'AN171', 28.2, 'AA17', 'bidirWalkway'),
        ('AN170', 'AN170T', 0.111, 'AA17', 'bidirWalkway'),
        ('AN171', 'AN171T', 0.111, 'AA17', 'bidirWalkway'),
        ('AN200', 'AN102', 15, 'AA18', 'escalatorUp'),
        ('AN102', 'AN200', 15, 'AA19', 'escalatorDown'),
        ('AN200', 'G61003', 12.3, 'AA20', 'bidirWalkway'),
        ('AN200', 'AN2022', 15.4, 'AA20', 'walkway'), #may be increased
        ('AN200', 'G61001', 24.0, 'AA20', 'bidirWalkway'),
        ('AN2122', 'AN152', 15, 'AA21', 'stairwayUp'),
        ('AN152', 'AN2122', 15, 'AA21', 'stairwayDown'),
        ('AN2122', 'AN2022', 1, 'AA22', 'walkway'), #previously 6.5m
        ('AN2022', 'G61002', 0.111, 'AA23', 'bidirWalkway'),  #G61002 check-out gate
        ('G61021', 'AN200', 15.4, 'AA23', 'walkway'),  #unidirectional walkway: G61021 check-in gate escalator side
        ('G61022', 'AN2122', 6.5, 'AA23', 'walkway'),  #unidirectional walkway: G61022 check-in gate stairway side
        ('AN200', 'AN201', 99, 'AA20', 'bidirWalkway'),
        ('AN2122', 'AN201', 99, 'AA23', 'bidirWalkway'),
        ('GTransAsdZ', 'AN201', 1, 'AA23', 'bidirWalkway') 
        }
        
        edgesShl={
        ('SN10', 'SN11', 18.9, 'SA1', 'bidirWalkway'),
        ('SN10', 'SN12', 17.8, 'SA1', 'bidirWalkway'),
        ('SN11', 'SN12', 12.7, 'SA1', 'bidirWalkway'),
        ('SN10', 'SN20', 30, 'SA2', 'bidirWalkway'),
        ('SN10', 'SN21', 16.3, 'SA2', 'bidirWalkway'),
        ('SN10', 'SN22', 16.3, 'SA2', 'bidirWalkway'),
        ('SN10', 'SN23', 30.4, 'SA2', 'bidirWalkway'),
        ('SN10', 'SN24', 30.2, 'SA2', 'bidirWalkway'),
        ('SN20', 'SN21', 15.8, 'SA2', 'bidirWalkway'),
        ('SN20', 'SN22', 16.7, 'SA2', 'bidirWalkway'),
        ('SN20', 'SN23', 3.5, 'SA2', 'bidirWalkway'),
        ('SN20', 'SN24', 4.7, 'SA2', 'bidirWalkway'),
        ('SN21', 'SN22', 12.8, 'SA2', 'bidirWalkway'),
        ('SN21', 'SN23', 15.1, 'SA2', 'bidirWalkway'),
        ('SN22', 'SN24', 15.3, 'SA2', 'bidirWalkway'),
        ('SN23', 'SN30', 23.2, 'SA3', 'bidirWalkway'),
        ('SN23', 'SN31', 11.7, 'SA3', 'bidirWalkway'),
        ('SN30', 'SN31', 11.7, 'SA3', 'bidirWalkway'),
        ('SN24', 'SN40', 23.2, 'SA4', 'bidirWalkway'),
        ('SN24', 'SN42', 11.9, 'SA4', 'bidirWalkway'),
        ('SN40', 'SN42', 11.9, 'SA4', 'bidirWalkway'),
        ('SN30', 'SN40', 8.2, 'SA5', 'bidirWalkway'),
        ('SN30', 'SN50', 12.9, 'SA5', 'bidirWalkway'),
        ('SN30', 'SN51', 6.4, 'SA5', 'bidirWalkway'),
        ('SN30', 'SN53', 12.4, 'SA5', 'bidirWalkway'),
        ('SN30', 'SN54', 14.8, 'SA5', 'bidirWalkway'),
        ('SN40', 'SN52', 6.8, 'SA5', 'bidirWalkway'),
        ('SN40', 'SN53', 14.8, 'SA5', 'bidirWalkway'),
        ('SN40', 'SN54', 12.3, 'SA5', 'bidirWalkway'),
        ('SN50', 'SN51', 8.1, 'SA5', 'bidirWalkway'),
        ('SN50', 'SN52', 9.7, 'SA5', 'bidirWalkway'),
        ('SN50', 'SN53', 3.6, 'SA5', 'bidirWalkway'),
        ('SN50', 'SN54', 4.7, 'SA5', 'bidirWalkway'),
        ('SN51', 'SN52', 12.9, 'SA5', 'bidirWalkway'),
        ('SN51', 'SN53', 6.4, 'SA5', 'bidirWalkway'),
        ('SN51', 'SN54', 11.8, 'SA5', 'bidirWalkway'),
        ('SN52', 'SN54', 6.8, 'SA5', 'bidirWalkway'),
        ('SN53', 'SN60', 28.7, 'SA6', 'bidirWalkway'),
        ('SN53', 'SN61', 14.5, 'SA6', 'bidirWalkway'),
        ('SN53', 'SN62', 15, 'SA6', 'bidirWalkway'),
        ('SN60', 'SN61', 14.5, 'SA6', 'bidirWalkway'),
        ('SN60', 'SN62', 14.5, 'SA6', 'bidirWalkway'),
        ('SN61', 'SN62', 5.4, 'SA6', 'bidirWalkway'),
        ('SN54', 'SN70', 28.7, 'SA7', 'bidirWalkway'),
        ('SN54', 'SN62', 15.3, 'SA7', 'bidirWalkway'),
        ('SN54', 'SN72', 14.9, 'SA7', 'bidirWalkway'),
        ('SN62', 'SN70', 15.1, 'SA7', 'bidirWalkway'),
        ('SN62', 'SN72', 7.6, 'SA7', 'bidirWalkway'),
        ('SN70', 'SN72', 14.7, 'SA7', 'bidirWalkway'),
        ('SN60', 'SN80', 27.2, 'SA8', 'bidirWalkway'),
        ('SN60', 'SN81', 13.7, 'SA8', 'bidirWalkway'),
        ('SN60', 'SN82', 6.6, 'SA8', 'bidirWalkway'),
        ('SN80', 'SN81', 13.7, 'SA8', 'bidirWalkway'),
        ('SN80', 'SN82', 21.9, 'SA8', 'bidirWalkway'),
        ('SN81', 'SN82', 9.7, 'SA8', 'bidirWalkway'),
        ('SN70', 'SN90', 27.2, 'SA9', 'bidirWalkway'),
        ('SN70', 'SN82', 7.2, 'SA9', 'bidirWalkway'),
        ('SN70', 'SN92', 13.9, 'SA9', 'bidirWalkway'),
        ('SN90', 'SN82', 22.1, 'SA9', 'bidirWalkway'),
        ('SN90', 'SN92', 13.9, 'SA9', 'bidirWalkway'),
        ('SN82', 'SN92', 11.0, 'SA9', 'bidirWalkway'),
        ('SN80', 'SN101', 7.1, 'SA10', 'bidirWalkway'),
        ('SN80', 'SN103', 13.7, 'SA10', 'bidirWalkway'),
        ('SN80', 'SN104', 3.6, 'SA10', 'bidirWalkway'),
        ('SN90', 'SN102', 7.4, 'SA10', 'bidirWalkway'),
        ('SN90', 'SN104', 4.7, 'SA10', 'bidirWalkway'),
        ('SN90', 'SN105', 13.7, 'SA10', 'bidirWalkway'),
        ('SN101', 'SN102', 13.0, 'SA10', 'bidirWalkway'),
        ('SN101', 'SN103', 7.1, 'SA10', 'bidirWalkway'),
        ('SN101', 'SN104', 8.8, 'SA10', 'bidirWalkway'),
        ('SN102', 'SN104', 10.0, 'SA10', 'bidirWalkway'),
        ('SN102', 'SN105', 7.4, 'SA10', 'bidirWalkway'),
        ('SN103', 'SN104', 14.2, 'SA10', 'bidirWalkway'),
        ('SN103', 'SN105', 8.3, 'SA10', 'bidirWalkway'),
        ('SN104', 'SN105', 14.5, 'SA10', 'bidirWalkway'),
        ('SN103', 'SN110', 23.2, 'SA11', 'bidirWalkway'),
        ('SN103', 'SN111', 11.8, 'SA11', 'bidirWalkway'),
        ('SN110', 'SN111', 11.7, 'SA11', 'bidirWalkway'),
        ('SN105', 'SN120', 23.2, 'SA12', 'bidirWalkway'),
        ('SN105', 'SN122', 12.0, 'SA12', 'bidirWalkway'),
        ('SN120', 'SN122', 12.0, 'SA12', 'bidirWalkway'),
        ('SN110', 'SN120', 8.4, 'SA13', 'bidirWalkway'),
        ('SN110', 'SN130', 30.4, 'SA13', 'bidirWalkway'),
        ('SN110', 'SN131', 15.1, 'SA13', 'bidirWalkway'),
        ('SN110', 'SN133', 3.7, 'SA13', 'bidirWalkway'),
        ('SN120', 'SN130', 30.2, 'SA13', 'bidirWalkway'),
        ('SN120', 'SN132', 15.3, 'SA13', 'bidirWalkway'),
        ('SN120', 'SN133', 4.7, 'SA13', 'bidirWalkway'),
        ('SN130', 'SN131', 16.4, 'SA13', 'bidirWalkway'),
        ('SN130', 'SN132', 16.4, 'SA13', 'bidirWalkway'),
        ('SN130', 'SN133', 30.0, 'SA13', 'bidirWalkway'),
        ('SN131', 'SN132', 13.2, 'SA13', 'bidirWalkway'),
        ('SN131', 'SN133', 16.0, 'SA13', 'bidirWalkway'),
        ('SN132', 'SN133', 16.8, 'SA13', 'bidirWalkway'),
        ('SN130', 'SN140', 30, 'SA14', 'bidirWalkway'),
        ('SN130', 'SN141', 16.4, 'SA14', 'bidirWalkway'),
        ('SN130', 'SN142', 16.4, 'SA14', 'bidirWalkway'),
        ('SN140', 'SN141', 16.4, 'SA14', 'bidirWalkway'),
        ('SN140', 'SN142', 16.4, 'SA14', 'bidirWalkway'),
        ('SN141', 'SN142', 13.2, 'SA14', 'bidirWalkway'),
        ('SN140', 'SN150', 30, 'SA15', 'bidirWalkway'),
        ('SN140', 'SN151', 16.4, 'SA15', 'bidirWalkway'),
        ('SN140', 'SN152', 16.4, 'SA15', 'bidirWalkway'),
        ('SN150', 'SN151', 16.4, 'SA15', 'bidirWalkway'),
        ('SN150', 'SN152', 16.4, 'SA15', 'bidirWalkway'),
        ('SN151', 'SN152', 13.3, 'SA15', 'bidirWalkway'),
        ('SN150', 'SN160', 30, 'SA16', 'bidirWalkway'),
        ('SN150', 'SN161', 16.4, 'SA16', 'bidirWalkway'),
        ('SN150', 'SN162', 16.4, 'SA16', 'bidirWalkway'),
        ('SN160', 'SN161', 16.5, 'SA16', 'bidirWalkway'),
        ('SN160', 'SN162', 16.4, 'SA16', 'bidirWalkway'),
        ('SN161', 'SN162', 13.4, 'SA16', 'bidirWalkway'),
        ('SN160', 'SN171', 16.3, 'SA17', 'bidirWalkway'),
        ('SN160', 'SN172', 16.5, 'SA17', 'bidirWalkway'),
        ('SN170', 'SN171', 16.5, 'SA17', 'bidirWalkway'),
        ('SN170', 'SN172', 16.2, 'SA17', 'bidirWalkway'),
        ('SN170', 'SN180', 30, 'SA18', 'bidirWalkway'),
        ('SN170', 'SN181', 16.1, 'SA18', 'bidirWalkway'),
        ('SN170', 'SN182', 16.6, 'SA18', 'bidirWalkway'),
        ('SN180', 'SN181', 16.6, 'SA18', 'bidirWalkway'),
        ('SN180', 'SN182', 16.1, 'SA18', 'bidirWalkway'),
        ('SN181', 'SN182', 13.1, 'SA18', 'bidirWalkway'),
        ('SN180', 'SN190', 30.1, 'SA19', 'bidirWalkway'),
        ('SN180', 'SN191', 16.0, 'SA19', 'bidirWalkway'),
        ('SN180', 'SN192', 16.8, 'SA19', 'bidirWalkway'),
        ('SN190', 'SN191', 16.9, 'SA19', 'bidirWalkway'),
        ('SN190', 'SN192', 15.9, 'SA19', 'bidirWalkway'),
        ('SN191', 'SN192', 13.2, 'SA19', 'bidirWalkway'),
        ('SN190', 'SN201', 15.4, 'SA20', 'bidirWalkway'),
        ('SN190', 'SN202', 16.6, 'SA20', 'bidirWalkway'),
        ('SN201', 'SN202', 13.6, 'SA20', 'bidirWalkway'),
        ('SN20', 'SN2122', 23.2, 'SA22', 'escalatorUp'),
        ('SN2122', 'SN20', 23.2, 'SA21', 'escalatorDown'),
        ('SN50', 'SN2324', 12.8, 'SA24', 'escalatorUp'),
        ('SN2324', 'SN50', 12.8, 'SA23', 'escalatorDown'),
        ('SN2526', 'SN104', 12.8, 'SA25', 'stairwayDown'),
        ('SN104', 'SN2526', 12.8, 'SA26', 'escalatorUp'),
        ('SN133', 'SN2728', 23.2, 'SA27', 'escalatorUp'),
        ('SN2728', 'SN133', 23.2, 'SA28', 'escalatorDown'),
        ('SN11', 'SN11T', 0.111, 'SA1', 'bidirWalkway'),
        ('SN21', 'SN21T', 0.111, 'SA2', 'bidirWalkway'),
        ('SN31', 'SN31T', 0.111, 'SA3', 'bidirWalkway'),
        ('SN51', 'SN51T', 0.111, 'SA5', 'bidirWalkway'),
        ('SN61', 'SN61T', 0.111, 'SA6', 'bidirWalkway'),
        ('SN81', 'SN81T', 0.111, 'SA8', 'bidirWalkway'),
        ('SN101', 'SN101T', 0.111, 'SA10', 'bidirWalkway'),
        ('SN111', 'SN111T', 0.111, 'SA11', 'bidirWalkway'),
        ('SN131', 'SN131T', 0.111, 'SA13', 'bidirWalkway'),
        ('SN141', 'SN141T', 0.111, 'SA14', 'bidirWalkway'),
        ('SN151', 'SN151T', 0.111, 'SA15', 'bidirWalkway'),
        ('SN161', 'SN161T', 0.111, 'SA16', 'bidirWalkway'),
        ('SN171', 'SN171T', 0.111, 'SA17', 'bidirWalkway'),
        ('SN181', 'SN181T', 0.111, 'SA18', 'bidirWalkway'),
        ('SN191', 'SN191T', 0.111, 'SA19', 'bidirWalkway'),
        ('SN201', 'SN201T', 0.111, 'SA20', 'bidirWalkway'),
        ('SN12', 'SN12T', 0.111, 'SA1', 'bidirWalkway'),
        ('SN22', 'SN22T', 0.111, 'SA2', 'bidirWalkway'),
        ('SN42', 'SN42T', 0.111, 'SA4', 'bidirWalkway'),
        ('SN52', 'SN52T', 0.111, 'SA5', 'bidirWalkway'),
        ('SN72', 'SN72T', 0.111, 'SA7', 'bidirWalkway'),
        ('SN92', 'SN92T', 0.111, 'SA9', 'bidirWalkway'),
        ('SN102', 'SN102T', 0.111, 'SA10', 'bidirWalkway'),
        ('SN122', 'SN122T', 0.111, 'SA12', 'bidirWalkway'),
        ('SN132', 'SN132T', 0.111, 'SA13', 'bidirWalkway'),
        ('SN142', 'SN142T', 0.111, 'SA14', 'bidirWalkway'),
        ('SN152', 'SN152T', 0.111, 'SA15', 'bidirWalkway'),
        ('SN162', 'SN162T', 0.111, 'SA16', 'bidirWalkway'),
        ('SN172', 'SN172T', 0.111, 'SA17', 'bidirWalkway'),
        ('SN182', 'SN182T', 0.111, 'SA18', 'bidirWalkway'),
        ('SN192', 'SN192T', 0.111, 'SA19', 'bidirWalkway'),
        ('SN202', 'SN202T', 0.111, 'SA20', 'bidirWalkway'),
        ('SN2122', 'GTransSchipholH', 100, 'SA30', 'bidirWalkway'),
        ('SN2324', 'GTransSchipholH', 100, 'SA30', 'bidirWalkway'),
        ('SN2526', 'GTransSchipholH', 100, 'SA30', 'bidirWalkway'),
        ('SN2728', 'GTransSchipholH', 100, 'SA30', 'bidirWalkway'),
        ('GTransSchiphol', 'GTransSchipholH', 1, 'SA30', 'bidirWalkway'),
        ('G561001H', 'SN2122', 10, 'SA30', 'bidirWalkway'), #50m
        ('G561002H', 'SN2122', 10, 'SA30', 'bidirWalkway'), #30m
        ('G561003H', 'SN2122', 5, 'SA30', 'bidirWalkway'),
        ('G561004H', 'SN2122', 10, 'SA30', 'bidirWalkway'), #40m
        ('G561005H', 'SN2122', 25, 'SA30', 'bidirWalkway'),
        ('G561001H', 'SN2324', 10, 'SA30', 'bidirWalkway'), #25m
        ('G561002H', 'SN2324', 10, 'SA30', 'bidirWalkway'), #20m
        ('G561003H', 'SN2324', 10, 'SA30', 'bidirWalkway'), #25m
        ('G561004H', 'SN2324', 10, 'SA30', 'bidirWalkway'), #30
        ('G561005H', 'SN2324', 3, 'SA30', 'bidirWalkway'),
        ('G561001H', 'SN2526', 10, 'SA30', 'bidirWalkway'),
        ('G561002H', 'SN2526', 10, 'SA30', 'bidirWalkway'), #20m
        ('G561003H', 'SN2526', 10, 'SA30', 'bidirWalkway'), #40m
        ('G561004H', 'SN2526', 10, 'SA30', 'bidirWalkway'), #30m
        ('G561005H', 'SN2526', 3, 'SA30', 'bidirWalkway'),
        ('G561001H', 'SN2728', 10, 'SA30', 'bidirWalkway'),
        ('G561002H', 'SN2728', 10, 'SA30', 'bidirWalkway'), #25m
        ('G561003H', 'SN2728', 10, 'SA30', 'bidirWalkway'), #50m
        ('G561004H', 'SN2728', 10, 'SA30', 'bidirWalkway'), #35m
        ('G561005H', 'SN2728', 3, 'SA30', 'bidirWalkway'),
        ('G561001', 'G561001H', 1, 'SA30', 'bidirWalkway'),
        ('G561002', 'G561002H', 1, 'SA30', 'bidirWalkway'),
        ('G561003', 'G561003H', 1, 'SA30', 'bidirWalkway'),
        ('G561004', 'G561004H', 1, 'SA30', 'bidirWalkway'),
        ('G561005', 'G561005H', 1, 'SA30', 'bidirWalkway'),
        }
        
        return edgesUpDown | edgesUtr | edgesBijl | edgesAsdZ | edgesShl
        
    def getAreas(self):    
        
        areasUpDown = {
            ('upA0', 99999, 'horizontal', 'Upstream'),
            ('downA0', 99999, 'horizontal', 'Downstream'),
            }
        
        areasUtr = {
            ('UA1', 362.7, 'horizontal', 'Utrecht'),
            ('UA2', 401, 'horizontal', 'Utrecht'),
            ('UA3', 420.3, 'horizontal', 'Utrecht'),
            ('UA4', 380, 'horizontal', 'Utrecht'),
            ('UA5', 429.9, 'horizontal', 'Utrecht'),
            ('UA6', 148.5, 'horizontal', 'Utrecht'),
            ('UA7', 223.6, 'horizontal', 'Utrecht'),
            ('UA8', 142.7, 'horizontal', 'Utrecht'),
            ('UA9', 226.5, 'horizontal', 'Utrecht'),
            ('UA10', 138.7, 'horizontal', 'Utrecht'),
            ('UA11', 228, 'horizontal', 'Utrecht'),
            ('UA12', 128, 'horizontal', 'Utrecht'),
            ('UA13', 200.6, 'horizontal', 'Utrecht'),
            ('UA14', 141.2, 'horizontal', 'Utrecht'),
            ('UA15', 230.6, 'horizontal', 'Utrecht'),
            ('UA16', 147.3, 'horizontal', 'Utrecht'),
            ('UA17', 235.1, 'horizontal', 'Utrecht'),
            ('UA18', 408.6, 'horizontal', 'Utrecht'),
            ('UA19', 342.8, 'horizontal', 'Utrecht'),
            ('UA20', 430.1, 'horizontal', 'Utrecht'),
            ('UA21', 32.8, 'stairway', 'Utrecht'),
            ('UA22', 38.7, 'stairway', 'Utrecht'),
            ('UA23', 40, 'stairway', 'Utrecht'),
            ('UA24', 13.5, 'escalator', 'Utrecht'),
            ('UA25', 13.5, 'escalator', 'Utrecht'),
            ('UA26', 13.4, 'escalator', 'Utrecht'),
            ('UA27', 13.4, 'escalator', 'Utrecht'),
            ('UA28', 41.9, 'stairway', 'Utrecht'),
            ('UA50', 8300, 'horizontal', 'Utrecht')
        }

        areasBijl={
            ('BA1', 384.2, 'horizontal', 'Bijlmer'),
            ('BA2', 429.3, 'horizontal', 'Bijlmer'),
            ('BA3', 142.4, 'horizontal', 'Bijlmer'),
            ('BA4', 143.5, 'horizontal', 'Bijlmer'),
            ('BA5', 159.2, 'horizontal', 'Bijlmer'),
            ('BA6', 154.2, 'horizontal', 'Bijlmer'),
            ('BA7', 162.7, 'horizontal', 'Bijlmer'),
            ('BA8', 150, 'horizontal', 'Bijlmer'),
            ('BA9', 129.3, 'horizontal', 'Bijlmer'),
            ('BA10', 125.7, 'horizontal', 'Bijlmer'),
            ('BA11', 417.4, 'horizontal', 'Bijlmer'),
            ('BA12', 414.4, 'horizontal', 'Bijlmer'),
            ('BA13', 402.6, 'horizontal', 'Bijlmer'),
            ('BA14', 316.3, 'horizontal', 'Bijlmer'),
            ('BA15', 764.6, 'horizontal', 'Bijlmer'),
            ('BA1617', 48.2, 'escalator', 'Bijlmer'),
            #('BA17', 24.1, 'escalator', 'Bijlmer'),
            ('BA18', 24.1, 'escalator', 'Bijlmer'),
            ('BA19', 2110, 'horizontal', 'Bijlmer'),
        }

        areasAsdZ = {
            ('AA1', 191.0, 'horizontal', 'AsdZ'),
            ('AA2', 65.0, 'stairway', 'AsdZ'),
            ('AA3', 346.6, 'horizontal', 'AsdZ'),
            ('AA4', 221.3, 'horizontal', 'AsdZ'),
            ('AA5', 224.3, 'horizontal', 'AsdZ'),
            ('AA6', 226.4, 'horizontal', 'AsdZ'),
            ('AA7', 219.9, 'horizontal', 'AsdZ'),
            ('AA8', 236.8, 'horizontal', 'AsdZ'),
            ('AA9', 187.1, 'horizontal', 'AsdZ'),
            ('AA10', 259.9, 'horizontal', 'AsdZ'),
            ('AA11', 59.7, 'horizontal', 'AsdZ'),
            ('AA12', 59.7, 'horizontal', 'AsdZ'),
            ('AA13', 68.75, 'horizontal', 'AsdZ'),
            ('AA14', 68.75, 'horizontal', 'AsdZ'),
            ('AA15', 229.6, 'horizontal', 'AsdZ'),
            ('AA16', 239.8, 'horizontal', 'AsdZ'),
            ('AA17', 448.2, 'horizontal', 'AsdZ'),
            ('AA18', 15.1, 'escalator', 'AsdZ'),
            ('AA19', 15.1, 'escalator', 'AsdZ'),
            ('AA20', 267.7, 'horizontal', 'AsdZ'),
            ('AA21', 45.5, 'stairway', 'AsdZ'),
            ('AA22', 40.2, 'horizontal', 'AsdZ'),
            ('AA23', 999, 'horizontal', 'AsdZ')
        }
        
        areasShl = {
            ('SA1', 395.5, 'horizontal', 'Schiphol'),
            ('SA2', 348.9, 'horizontal', 'Schiphol'),
            ('SA3', 69.9, 'horizontal', 'Schiphol'),
            ('SA4', 121.4, 'horizontal', 'Schiphol'),
            ('SA5', 146.7, 'horizontal', 'Schiphol'),
            ('SA6', 112.2, 'horizontal', 'Schiphol'),
            ('SA7', 174.8, 'horizontal', 'Schiphol'),
            ('SA8', 104.8, 'horizontal', 'Schiphol'),
            ('SA9', 163.1, 'horizontal', 'Schiphol'),
            ('SA10', 174, 'horizontal', 'Schiphol'),
            ('SA11', 75.2, 'horizontal', 'Schiphol'),
            ('SA12', 121.9, 'horizontal', 'Schiphol'),
            ('SA13', 361.2, 'horizontal', 'Schiphol'),
            ('SA14', 353.1, 'horizontal', 'Schiphol'),
            ('SA15', 359.6, 'horizontal', 'Schiphol'),
            ('SA16', 361.3, 'horizontal', 'Schiphol'),
            ('SA17', 309.8, 'horizontal', 'Schiphol'),
            ('SA18', 356, 'horizontal', 'Schiphol'),
            ('SA19', 361.1, 'horizontal', 'Schiphol'),
            ('SA20', 353.6, 'horizontal', 'Schiphol'),
            ('SA21', 23.2, 'escalator', 'Schiphol'),
            ('SA22', 23.2, 'escalator', 'Schiphol'),
            ('SA23', 12.8, 'escalator', 'Schiphol'),
            ('SA24', 12.8, 'escalator', 'Schiphol'),
            ('SA25', 12.8*1.5, 'stairway', 'Schiphol'),
            ('SA26', 12.8, 'escalator', 'Schiphol'),
            ('SA27', 23.2, 'escalator', 'Schiphol'),
            ('SA28', 23.2, 'escalator', 'Schiphol'),
            ('SA30', 9999, 'horizontal', 'Schiphol')
        }
        
        return areasUpDown | areasUtr | areasBijl | areasAsdZ | areasShl;
    
    def getAreaInterfaces(self):
        
        interfacesAsdZ = {
            ('AA1', 'AA2', 6*0.8 ), #stairwayUp
            ('AA2', 'AA3', 6*0.95), #stairwayDown
            ('AA18', 'AA20', 1*1.25 ), #escalator
            ('AA10', 'AA19', 1*1.25 ), #escalator
            ('AA10', 'AA11', 2.4*1.2), #level walkway
            ('AA10', 'AA12', 2.4*1.2), #level walkway
            ('AA13', 'AA15', 2.4*1.2), #level walkway
            ('AA14', 'AA15', 2.4*1.2), #level walkway
            ('AA22', 'AA21', 3*0.8 ), #stairwayUp
            ('AA15', 'AA21', 3*0.95 ) #stairwayDown 
        }
    
        interfacesBijlmer = {
            ('BA2', 'BA3', 5.5*1.2), #level walkway
            ('BA2', 'BA4', 5.5*1.2), #level walkway
            ('BA9', 'BA11', 4.5*1.2), #level walkway
            ('BA10', 'BA11', 4.5*1.2), #level walkway
            ('BA11', 'BA1617', 2*1.25), #escalator (double)
            ('BA19', 'BA18', 1*1.25) #escalator
        }
        
        interfacesUtrecht = {
            ('UA1', 'UA21', 5.6*0.95), #stairway down
            ('UA50', 'UA21', 5.6*0.8), #stairway up
            ('UA5', 'UA22', 3.5*0.95), #stairway down
            ('UA50', 'UA22', 3.5*0.8), #stairway up
            ('UA5', 'UA6', 2.9*1.2), #level walkway
            ('UA5', 'UA7', 8*1.2), #level walkway
            ('UA16', 'UA18', 2.2*1.2), #level walkway
            ('UA17', 'UA18', 8.4*1.2), #level walkway
            ('UA6', 'UA23', 3.3*0.8), #stairway up
            ('UA50', 'UA23', 3.3*0.95), #stairway down
            ('UA50', 'UA24', 1*1.25), #escalator down
            ('UA8', 'UA25', 1*1.25), #escalator up
            ('UA12', 'UA26', 1*1.25), #escalator up
            ('UA50', 'UA27', 1*1.25), #escalator down
            ('UA50', 'UA28', 3.6*0.95), #stairway down
            ('UA13', 'UA28', 3.6*0.8), #stairway up
        }
        
        interfacesSchiphol = {
            ('SA2', 'SA3', 3.4*1.2), #level walkway
            ('SA2', 'SA4', 5.7*1.2), #level walkway
            ('SA3', 'SA5', 3.5*1.2), #level walkway
            ('SA4', 'SA5', 5.7*1.2), #level walkway
            ('SA5', 'SA6', 3.5*1.2), #level walkway
            ('SA5', 'SA7', 5.8*1.2), #level walkway
            ('SA8', 'SA10', 3.7*1.2), #level walkway
            ('SA9', 'SA10', 5.7*1.2), #level walkway
            ('SA10', 'SA11', 3.7*1.2), #level walkway
            ('SA10', 'SA12', 5.7*1.2), #level walkway
            ('SA11', 'SA13', 3.8*1.2), #level walkway
            ('SA12', 'SA13', 5.7*1.2), #level walkway
            ('SA2', 'SA22', 1*1.25), #escalator
            ('SA30', 'SA21', 1*1.25), #escalator
            ('SA5', 'SA24', 1*1.25), #escalator
            ('SA30', 'SA23', 1*1.25), #escalator
            ('SA30', 'SA25', 1.5*0.95), #stairway down
            ('SA10', 'SA26', 1*1.25), #escalator
            ('SA13', 'SA27', 1*1.25), #escalator
            ('SA30', 'SA28', 1*1.25) #escalator
        }
        
        return interfacesAsdZ | interfacesBijlmer | interfacesUtrecht | interfacesSchiphol;
    
    def getPedPaths(self):
        
        pedPaths = [
                ['Gup', 'upN0', 'upN0T'],
                #['AN110T', 'AN110', 'AN1011', 'AN102', 'AN200', 'AN2022', 'G61002'],
                ['AN110T', 'AN110', 'AN1113', 'AN1315', 'AN152', 'AN2122', 'AN2022', 'G61002'],
                #['AN120T', 'AN120', 'AN1012', 'AN102', 'AN200', 'AN2022', 'G61002'],
                ['AN120T', 'AN120', 'AN1114', 'AN1415', 'AN152', 'AN2122', 'AN2022', 'G61002'],
                ['downN0T', 'downN0', 'Gdown']
            ]
        
        return pedPaths
    
    def setPlatformAttributes(self):
        
        self.platformAttributes = dict()
        
        interfaceNodes = {'BP2': {'BN11T', 'BN21T', 'BN31T', 'BN51T', 'BN71T', 'BN91T', 'BN111T', 'BN121T', 'BN131T', 'BN141T', 'BN151T'},
        'BP3': {'BN12T', 'BN22T', 'BN43T', 'BN63T', 'BN83T', 'BN103T', 'BN113T', 'BN123T', 'BN133T', 'BN143T', 'BN153T'},
        'AP4': {'AN30T', 'AN40T', 'AN50T', 'AN60T', 'AN70T', 'AN80T', 'AN90T', 'AN100T', 'AN110T', 'AN130T', 'AN150T', 'AN160T', 'AN170T'},
        'AP3': {'AN31T', 'AN41T', 'AN51T', 'AN61T', 'AN71T', 'AN81T', 'AN91T', 'AN101T', 'AN120T', 'AN140T', 'AN151T', 'AN161T', 'AN171T'},
        'UP5': {'UN21T', 'UN31T', 'UN41T', 'UN51T', 'UN61T', 'UN81T', 'UN101T', 'UN121T', 'UN141T', 'UN161T', 'UN181T', 'UN191T', 'UN201T'},
        'UP7': {'UN22T', 'UN32T', 'UN42T', 'UN52T', 'UN72T', 'UN92T', 'UN112T', 'UN132T', 'UN152T', 'UN172T', 'UN182T', 'UN192T', 'UN202T'},
        'SP3': {'SN11T', 'SN21T', 'SN31T', 'SN51T', 'SN61T', 'SN81T', 'SN101T', 'SN111T', 'SN131T', 'SN141T', 'SN151T', 'SN161T', 'SN171T', 'SN181T', 'SN191T', 'SN201T'},
        'SP4': {'SN12T', 'SN22T', 'SN42T', 'SN52T', 'SN72T', 'SN92T', 'SN102T', 'SN122T', 'SN132T', 'SN142T', 'SN152T', 'SN162T', 'SN172T', 'SN182T', 'SN192T', 'SN202T'},
        'upP0': {'upN0T'},
        'downP0': {'downN0T'}}
        
        assert(Parameter.upstreamPlatform in interfaceNodes), \
        "upstream platform (%s, defined in Parameters) missing in interfaceNodes" % Parameter.upstreamPlatform
        
        assert(Parameter.downstreamPlatform in interfaceNodes), \
        "downstream platform (%s, defined in Parameters) missing in interfaceNodes" % Parameter.downstreamPlatform
        
        self.platformAttributes["interfaceNodes"] = interfaceNodes
        platformNameSet = set(interfaceNodes.keys())
        self.platformAttributes["platformNames"] = platformNameSet
        
        #check if interface nodes are in list of nodes:
        for nodeSet in interfaceNodes.values():
            for node in nodeSet:
                assert(node in self.nodes), "node %s not in node set"
        
        areaLimits = {'BN11T': [-129.7, -86.9], 'BN21T': [-86.9, -56.9],
        'BN31T': [-56.9, -28.4], 'BN51T': [-28.4, 0], 'BN71T': [0, 28.2],
        'BN91T': [28.2, 56.4], 'BN111T': [56.4, 86.4], 'BN121T': [86.4, 116.4],
        'BN131T': [116.4, 146.4], 'BN141T': [146.4, 176.4], 'BN151T': [176.4, 239.4],
        'AN30T': [-286.5, -240], 'AN40T': [-240, -210], 'AN50T': [-210, -180],
        'AN60T': [-180, -150], 'AN70T': [-150, -120], 'AN80T': [-120, -90],
        'AN90T': [-90, -60], 'AN100T': [-60, -27.3], 'AN110T': [-27.3, 0],
        'AN130T': [0, 31.2], 'AN150T': [31.2, 60], 'AN160T': [60, 90],
        'AN170T': [90, 145.6], 'UN21T': [-180.8, -150], 'UN31T': [-150, -120],
        'UN41T': [-120, -90], 'UN51T': [-90, -60], 'UN61T': [-60, -30],
        'UN81T': [-30, 0], 'UN101T': [0, 30], 'UN121T': [30, 60], 'UN141T': [60, 90],
        'UN161T': [90, 120], 'UN181T': [120, 150], 'UN191T': [150, 180],
        'UN201T': [180, 235], 'BN12T': [-129.7, -86.9], 'BN22T': [-86.9, -56.9],
        'BN43T': [-56.9, -28.4], 'BN63T': [-28.4, 0], 'BN83T': [0, 28.2],
        'BN103T': [28.2, 56.4], 'BN113T': [56.4, 86.4], 'BN123T': [86.4, 116.4],
        'BN133T': [116.4, 146.4], 'BN143T': [146.4, 176.4], 'BN153T': [176.4, 239.4],
        'AN31T': [-286.5, -240], 'AN41T': [-240, -210], 'AN51T': [-210, -180],
        'AN61T': [-180, -150], 'AN71T': [-150, -120], 'AN81T': [-120, -90],
        'AN91T': [-90, -60], 'AN101T': [-60, -27.3], 'AN120T': [-27.3, 0],
        'AN140T': [0, 31.2], 'AN151T': [31.2, 60], 'AN161T': [60, 90],
        'AN171T': [90, 145.6], 'UN22T': [-180.8, -150], 'UN32T': [-150, -120],
        'UN42T': [-120, -90], 'UN52T': [-90, -60], 'UN72T': [-60, -30],
        'UN92T': [-30, 0], 'UN112T': [0, 30], 'UN132T': [30, 60], 'UN152T': [60, 90],
        'UN172T': [90, 120], 'UN182T': [120, 150], 'UN192T': [150, 180],
        'UN202T': [180, 235], 'SN11T': [-198.5,-162.9], 'SN21T': [-162.9,-132.9],
        'SN31T': [-132.9,-109.7], 'SN51T': [-109.7,-97.36], 'SN61T': [-97.36,-68.66],
        'SN81T': [-68.66,-41.46], 'SN101T': [-41.46,-27.77], 'SN111T': [-27.77,-4.564],
        'SN131T': [-4.564,25.436], 'SN141T': [25.436,55.436], 'SN151T': [55.436,85.436],
        'SN161T': [85.436,115.436], 'SN171T': [115.436,145.436], 'SN181T': [145.436,175.436],
        'SN191T': [175.436,205.436], 'SN201T': [205.436,234.1], 'SN12T': [-196.3,-162.9],
        'SN22T': [-162.9,-132.9], 'SN42T': [-132.9,-109.7], 'SN52T': [-109.7,-97.36],
        'SN72T': [-97.36,-68.66], 'SN92T': [-68.66,-41.46], 'SN102T': [-41.46,-27.77],
        'SN122T': [-27.77,-4.564], 'SN132T': [-4.564,25.436], 'SN142T': [25.436,55.436],
        'SN152T': [55.436,85.436], 'SN162T': [85.436,115.436], 'SN172T': [115.436,145.436],
        'SN182T': [145.436,175.436], 'SN192T': [175.436,205.436], 'SN202T': [205.436,232.7],
        'upN0T': [-999,999], 'downN0T': [-999,999]}
        
        self.platformAttributes["areaLimits"] = areaLimits
        
        for interfaceNode in areaLimits.keys():
            assert(interfaceNode in self.nodes), "node %s not in node set" % interfaceNode
        
        stopSignalPos = {
            'UP7': {4: -39.4, 6: -72.7, 8: -96.7, 10: -144.7, 12: -180.8},
            'UP5': {4: -39.4, 6: -72.7, 8: -120.7, 10: -168.7, 12: -180.8},
            'BP2': {4: 1.2, 6: -51.3, 8: -83, 10: -107.4, 12: -107.4},
            'BP3': {4: 1.2, 6: -51.3, 8: -83, 10: -107.4, 12: -107.4},
            'AP3': {4: -36.4, 6: -60, 8: -110.5, 10: -168.3, 12: -224},
            'AP4': {4: -36.4, 6: -60, 8: -110.5, 10: -168.3, 12: -224},
            'SP3': {6: -147.092, 10: -147.092, 12: -159.631},
            'SP4': {2: -85.708, 4: -42.564, 6: 0.361, 8: 36.597, 10: 88.928, 12: 141.355},
            'upP0': {4: 0, 6: 0, 8: 0, 10: 0, 12: 0},
            'downP0': {4: 0, 6: 0, 8: 0, 10: 0, 12: 0}
            }
        
        self.platformAttributes["stopSignalPos"] = stopSignalPos
        
        for platform in stopSignalPos.keys():
            assert(platform in platformNameSet), "platform %s not in platformSet" % platform
        
        usageDirection = {'BP2': 'left', 'BP3': 'left', 'AP4': 'left',
                          'AP3': 'left', 'UP5': 'left', 'UP7': 'left',
                          'SP3': 'left', 'SP4': 'right',
                          'upP0': 'left', 'downP0': 'left'}
        
        for platform, direction in usageDirection.items():
            assert(platform in platformNameSet), "platform %s not in platformSet" % platform
            assert(direction == "right" or direction == "left"), "invalid direction (%s)" % direction
        
        self.platformAttributes["usageDirection"] = usageDirection