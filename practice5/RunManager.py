from IndexMode import IndexMode
from typing import Generator, List, Set
import itertools
import re
import operator
from nltk.corpus import stopwords

from index import IndexStore, RankedRetrivialAnswer, RankedRetrivialAnswerParent
import numpy as np
import random


class RunManager(object):
    def __init__(self, options, index, docCount, docList):
        self.options = options
        self.index: IndexStore = index
        self.groupId = "NassimThomasAntoineMelanie"
        self.docCount = docCount
        self.docIDList = docList
        self.granularity = ["article", "elements", "passages"]
        self.stop = ["nostop", "stop" +
                     str(len(set(stopwords.words('english'))))]
        self.stem = ["nostem", "porter"]
        self.algorithms = [
            IndexMode.SMART_LTN,
            IndexMode.SMART_LTC,
        ]

    def run(self):
        "Run the retrieval document listing"
        _lines = self.readFile()
        print(len(_lines))
        self.computeLTN_LTC()
        _indexTerms = list(self.index.objects.keys())
        _fixK1 = [(1.2, float("{:.2f}".format(_b)))
                  for _b in list(np.arange(0.0, 1.1, 0.1))]
        _fixB = [(float("{:.2f}".format(_k1)), 0.75)
                 for _k1 in list(np.arange(0.0, 4.2, 0.2))]

        _bm25Parameters = _fixK1 + _fixB
        for _paramId, _paramRun in enumerate(_bm25Parameters):
            self.index.compute_bm25(k1=_paramRun[0], b=_paramRun[1])
            for _line in _lines:
                self.index.RSV={}
                
                _topicId, *_query = _line.strip().split()
                answer = self.index.compute_ranked_retrieval_as_list(
                    " ".join(_query))
                
                for _answerDoc in answer :
                    _ll =_answerDoc.doc.split("/")
                    self.manageRSVDic(docParent= _answerDoc.doc, rsv=_answerDoc.wtdsum, splitedList=  _ll)
        
                self.sortRSVDict()
                self.writeRunsFiles( paramId= _paramId, topicId= _topicId , param=[_paramRun[0] , _paramRun[1]]) 

        for _runID, _algo in enumerate(self.algorithms):
            self.index.indexMode = _algo
            for _line in _lines:
                self.index.RSV={}
                _topicId, *_query = _line.strip().split()
                for _queryword in _query:
                    if _queryword in _indexTerms:
                        self.index.setQueryTermFrequency(_queryword)
                for _docNum in self.docIDList:
                    
                    _rsv = 0
                    for _qterm in self.index.queryTermManager:
                        _qwordProp = self.index.objects[_qterm]
                        if self.index.indexMode == IndexMode.SMART_LTN and _docNum in list(_qwordProp.smart_ltn.keys()):
                            _rsv = _rsv + \
                                (_qwordProp.smart_ltn[_docNum] *
                                 self.index.queryTermManager[_qterm])
                        if self.index.indexMode == IndexMode.SMART_LTC and _docNum in list(_qwordProp.smart_ltc.keys()):
                            _rsv = _rsv + \
                                (_qwordProp.smart_ltc[_docNum] *
                                 self.index.queryTermManager[_qterm])
                    if _rsv==0:
                        continue
                    _ll =_docNum.split("/")
                    _parentDoc=_docNum.split("/")[0]
                    
                    self.manageRSVDic(docParent=_docNum ,rsv= _rsv,splitedList=_ll)
                    
                    
                self.sortRSVDict()
                self.writeRunsFiles(algo=_algo.name , paramId= _runID, topicId=_topicId)
                

    def writeRunsFiles(self, paramId, topicId, algo="BM25" , param=None ):
        _i=1
        _paramStr=""
        if param:
            _paramStr="_k{}_b{}".format(param[0], param[1])
        for _documentRank, _doc in self.index.RSV.items():
            _f = open("{}_{}_{}_{}_title_id_categories_revision_contributor_timestamp_username_bdy_{}_{}{}.txt".format(self.options.dpath+self.groupId, str(paramId+1), algo,
                                                                self.granularity[1], self.stop[1] if self.options.stopwords else self.stop[0], self.stem[1] if self.options.stemmer else self.stem[0], _paramStr ), "a")
            for _idc,_childy in enumerate(_doc.childrenStat.children):
                
                _f.write(topicId+" Q0 " + _documentRank+" "+str(_i)+" "+str(
                            list(_childy.values())[0])+" "+self.groupId+algo+" {}\n".format( list(_childy.keys())[0] ))
                _i=_i+1
                if _i == 1501:
                    break
                    
            _f.close()
            if _i == 1501:
                break

    def sortRSVDict(self):
        self.index.RSV=  dict(map(lambda x: self.sortedChildrenScore(x) , self.index.RSV.items() )) 
                
        self.index.RSV = dict(sorted(self.index.RSV.items(), key= lambda x: self.sortedParentScore(x), reverse=True))   
                        
    
    def manageRSVDic(self, docParent, splitedList , rsv ):
        if docParent in self.index.RSV:
            _answer :RankedRetrivialAnswerParent =self.index.RSV[splitedList[0]]
            _answer.childrenStat.children.append({docParent:rsv})
            _answer.parentScore = _answer.parentScore + (self.getAlphaCoefself( splitedList[len(splitedList)-1] ) * rsv) 
            self.index.RSV.update( { splitedList[0]: _answer })
        else:
            _answerParent=RankedRetrivialAnswerParent()
            _answerParent.childrenStat=RankedRetrivialAnswer()
            _answerParent.childrenStat.children.append({docParent:rsv})
            _answerParent.parentScore=self.getAlphaCoefself( splitedList[len(splitedList)-1] ) * rsv
            self.index.RSV.update({splitedList[0]: _answerParent})
                        
        self.index.RSV=  dict(map(lambda x: self.sortedChildrenScore(x) , self.index.RSV.items() )) 
                
        self.index.RSV = dict(sorted(self.index.RSV.items(), key= lambda x: self.sortedParentScore(x), reverse=True))
    def sortedChildrenScore(self,x):
        _parentDoc,_answerParent=x    
        _answerParent.childrenStat.children=sorted(_answerParent.childrenStat.children , key= lambda child:list(child.values())[0], reverse=True)
        
        return (_parentDoc , _answerParent)      
    def sortedParentScore(self,x):
        _parentDoc,_answerParent=x
        return _answerParent.parentScore
        
          
    def getAlphaCoefself(self,sectionName):
        if sectionName == "title" :
            return 4
        elif sectionName == "categories":
            return 3
        elif sectionName == "revision":
            return 2
        elif sectionName == "id":
            return 2
        elif sectionName == "username":
            return 2.5
        elif sectionName == "timestamp":
            return 1.5
        elif sectionName == "contributor":
            return 2.8
        elif sectionName == "bdy":
            return 1
        
            
        
    
    def readFile(self):
        "Read topic file "
        _file = open(self.options.topics, 'r')
        return _file.readlines()

    def computeLTN_LTC(self):
        "Compute Smart LTN and LTC"
        for word in sorted(self.index.objects):
            _wordProperties = self.index.objects[word]
            # Fill in SMART LTN Values
            _wordProperties.smartLTN_values(self.docCount, self.index, True)
            # Fill in SMART LTC Values
            _wordProperties.smartLTC_values(self.index)
