from IndexMode import IndexMode
from typing import Generator, List, Set
import itertools
import re
import operator
from nltk.corpus import stopwords

from index import IndexStore
import numpy as np
import random
class RunManager(object):
    def __init__(self, options, index, docCount, docList):
        self.options = options
        self.index : IndexStore= index 
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
        _fixK1=[( 1.2 , float("{:.2f}".format(_b)) ) for _b in list(np.arange(0.0, 1.1, 0.1))]
        _fixB=[( float("{:.2f}".format(_k1))  , 0.75 ) for _k1 in list(np.arange(0.0, 4.2, 0.2))]
        
        _bm25Parameters= _fixK1 + _fixB
        for _paramId, _paramRun in enumerate(_bm25Parameters) : 
            self.index.compute_bm25(k1=_paramRun[0], b=_paramRun[1])
            for _line in _lines:
                _topicId, *_query = _line.strip().split()
                answer = self.index.compute_ranked_retrieval_as_list(" ".join(_query) )
                for _i , a in enumerate(itertools.islice(answer, 1500)):
                    _f = open("{}_{}_{}_{}_{}_{}_k{}_b{}.txt".format(self.options.dpath+self.groupId,str(_paramId+1),"BM25",
                    self.granularity[0],self.stop[1] if self.options.stopwords else self.stop[0],self.stem[1] if self.options.stemmer else self.stem[0],_paramRun[0],_paramRun[1]), "a")
                    _f.write(_topicId+" Q0 "+ a.doc+" "+str(_i+1)+" "+str(a.wtdsum)+" "+self.groupId+"BM25"+" /article[1]\n")
                    _f.close()# index query words
        
        for _runID, _algo in enumerate(self.algorithms):
            self.index.indexMode=_algo
            _bm25Parameters=[(float("%.2f" % round(random.uniform(0.0,31.0),1)) , float("%.2f" % round(random.random(),2)) ) for _ in range(31)]
            for _line in _lines:
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
                    self.index.RSV.update({_docNum: _rsv})

                # return 1500
                _dicOrdered = dict(
                    sorted(self.index.RSV.items(), key=operator.itemgetter(1), reverse=True))
                _dic = dict(itertools.islice(_dicOrdered.items(), 1500))
                for _documentRank , _doc in enumerate(_dic):
                    _f = open("{}_{}_{}_{}_{}_{}.txt".format(self.options.dpath+self.groupId,str(_runID+1),_algo.name,
                            self.granularity[0],self.stop[1] if self.options.stopwords else self.stop[0],self.stem[1] if self.options.stemmer else self.stem[0]), "a")
                    _f.write(_topicId+" Q0 "+ _doc+" "+str(_documentRank+1)+" "+str(_dic[_doc])+" "+self.groupId+_algo.name+" /article[1]\n")
                    _f.close()
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
        
