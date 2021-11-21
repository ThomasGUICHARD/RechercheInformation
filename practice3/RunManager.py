from IndexMode import IndexMode
from typing import Generator, List, Set
import itertools
import re
import operator
from nltk.corpus import stopwords


class RunManager(object):
    def __init__(self, options, index, docCount, docList):
        self.options = options
        self.index = index
        self.groupId = "NassimThomasAntoineMelanie"
        self.docCount = docCount
        self.docIDList = docList
        self.granularity = ["article", "elements", "passages"]
        self.stop = ["nostop", "stop" +
                     str(len(set(stopwords.words('english'))))]
        self.stem = ["nostem", "porter"]
        self.algorithms = [IndexMode.SMART_LTN,
                           IndexMode.SMART_LTC]  # TODO : add BM25

    def run(self):
        _lines = self.readFile()
        self.computeLTN_LTC()
        _indexTerms = list(self.index.objects.keys())
        # index query words
        for _runID, _algo in enumerate(self.algorithms):
            self.index.indexMode=_algo
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
        _file = open(self.options.topics, 'r')
        return _file.readlines()
    def computeLTN_LTC(self):
        for word in sorted(self.index.objects):
            _wordProperties = self.index.objects[word]
            # Fill in SMART LTN Values
            _wordProperties.smartLTN_values(self.docCount, self.index, True)
            # Fill in SMART LTC Values
            _wordProperties.smartLTC_values(self.index)
        
