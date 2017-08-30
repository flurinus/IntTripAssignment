class Activity(object):


    def __init__(self, actType,param):
        self.actType = actType
        self.param = param
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return self.actType + ": " + str(self.param)