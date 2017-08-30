from board import Board
from parameter import Parameter
import sys


dateList = ['2017-03-08', '2017-03-09', '2017-03-14', '2017-03-15', '2017-03-16', \
            '2017-03-21', '2017-03-22', '2017-03-23', '2017-03-28', '2017-03-29', '2017-03-30']    

for caseStudyDate in dateList:
    #model and case study parameters
    param = Parameter(caseStudyDate)
    Board(param)