
import re
import os
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import numpy
import pyspark
from matplotlib import pyplot
from pyspark.sql import SparkSession
import time
class SearchEngine():
    def __init__(self,dataDirectory):
        self.regexDocument="<doc><docno>(.*)<\/docno>([\s a-zA-Z0-9 ^’ù*$!:#;@}{,.?\*\"\|\'\(\[\]\)\/-]*)<\/doc>"
        self.listDocument=[]
        self.rddListDocument=None
        self.listDocumentData=[]
        self.rddListDocumentData=None
        self.tf = CountVectorizer(stop_words=nltk.corpus.stopwords.words('english'))
        self.stop_words = nltk.corpus.stopwords.words('english')
        self.tf_matrix=None
        self.feature_names=[]
        self.incidenceMatrix=None
        self.generatedDictionary={}
        self.dataDirectory=dataDirectory
        self.time=0
        self.spark = SparkSession.builder.appName('SparkByExamples.com').getOrCreate()
        self.sc=self.spark.sparkContext
        self.timelist =[]
        self.porterStemmer=PorterStemmer()
    def setListDocument(self):
        for filename in os.listdir(self.dataDirectory):
            print(filename)
            _file=open("{}/{}".format(self.dataDirectory,filename), "r")
            _dataFile=_file.read()
            self.listDocument.extend(re.findall( self.regexDocument , _dataFile))
        self.rddListDocument=self.sc.parallelize(self.listDocument)
        self.rddListDocumentData=self.rddListDocument.map(lambda x : x[1])
        # e=map(self.statisticsDocuments,self.rddListDocument.collect())
        # print(list(e))
    def statisticsDocuments(self,x):
        return "DocumentId : {} \nDocumentLength : {}".format(x[0],len(x[1]))
    def setMatrixIncidence(self):
        self.tf_matrix = self.tf.fit_transform(self.rddListDocumentData.collect())
        self.feature_names=self.tf.get_feature_names_out()
        # self.feature_names=[ self.porterStemmer.stem(x) for x in  self.feature_names]
        print("term length : {}".format(len(self.feature_names)))
        self.incidenceMatrix= self.tf_matrix.A
    def setGeneratedDictionary(self):
        for _id , _word in enumerate(self.feature_names) :
            self.generatedDictionary[_word]=[]
            _columnOccurance=self.incidenceMatrix[:,_id]
            for _idOccurence , _docNBR in enumerate(_columnOccurance):
                if _docNBR !=0 :
                    _list=self.generatedDictionary[_word]
                    _list.append("fr:{}  D{}".format(_docNBR,_idOccurence))
                    self.generatedDictionary[_word]=_list
    def run(self):
        
        
        start_time=time.time()
        self.setListDocument()
        self.setMatrixIncidence()
        self.setGeneratedDictionary()
        print(self.generatedDictionary)
        # print(self.generatedDictionary)    
        print(time.time() - start_time)

        # # print(self.timelist)
        # barWidth = 0.25
        # # set height of bar
        # bars1 = [1.7290585041046143,1.706298589706421,1.667466640472412,1.6934142112731934,2.011308193206787,3.685555934906006,4.840803623199463,1.246026039123535]
        
        # # Set position of bar on X axis
        # r1 = numpy.arange(8)

        # # Make the plot
        # pyplot.bar(r1, bars1, color='#00ff00', width=barWidth,
        #         edgecolor='white')
        

        # # Add xticks on the middle of the group bars
        # pyplot.xlabel('Fichier', fontweight='bold')
        # pyplot.ylabel('Running Time', fontweight='bold')
        # pyplot.xticks([r  for r in range(len(bars1))], ["01","02","03","04","05","06","07","08"])
        # # Create legend & Show graphic
        # pyplot.legend()
        # pyplot.show()
    
_searchEngine=SearchEngine(dataDirectory="Practice_02_data")
_searchEngine.run()     