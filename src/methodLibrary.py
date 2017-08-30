from numpy.random import choice
import pickle

def weightedChoice(elemDict, normalize=False):
        
        elemIDList = list()
        elemProbList = list()
        
        if normalize:
            totProb = 0
                
        for elemID, choiceProb in elemDict.items():
            elemIDList.append(elemID)
            elemProbList.append(choiceProb)
            
            if normalize:
                totProb += choiceProb
        
        if normalize:
            assert(totProb > 0), "all alternatives have zero probability: %s" % elemDict

            for elemID,elemProb in enumerate(elemProbList):
                elemProbList[elemID] = elemProb/totProb
            
        #use numpy.random.choice to draw from weighted distribution
        return choice(elemIDList, p=elemProbList)
    
def saveObject(obj, filename):
    with open(filename, 'wb') as outputStream:
        pickle.dump(obj, outputStream, pickle.HIGHEST_PROTOCOL)

def loadObject(filename):
    with open(filename, 'rb') as inputStream:
        return pickle.load(inputStream)
