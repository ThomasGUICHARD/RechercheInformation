
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
        self.tf = CountVectorizer(stop_words=nltk.corpus.stopwords.words('english')) # if we want to search with stopwords we have juste to remove the CountVectorizer parameter 
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
        self.collectionStats={"termCollectionFrenquency":[]}
    def setListDocument(self):
        for filename in os.listdir(self.dataDirectory):
            print(filename)
            _file=open("{}/{}".format(self.dataDirectory,filename), "r")
            _dataFile=_file.read()
            self.listDocument.extend(re.findall( self.regexDocument , _dataFile))
        self.rddListDocument=self.sc.parallelize(self.listDocument)
        self.rddListDocumentData=self.rddListDocument.map(lambda x : x[1])
        e=list(map(self.statisticsDocuments,self.rddListDocument.collect()))
        self.collectionStats["documentLenghtStats"]=e
    def statisticsDocuments(self,x):
        return {"DocumentId" :x[0]  , "DocumentLength" : len(x[1])}
    def setMatrixIncidence(self):
        self.tf_matrix = self.tf.fit_transform(self.rddListDocumentData.collect())
        self.feature_names=self.tf.get_feature_names_out()
        # self.feature_names=[ self.porterStemmer.stem(x) for x in  self.feature_names]  FOR PORTER STEMMER !!
        
        self.collectionStats["VocabularySize"]=len(self.feature_names)
        self.incidenceMatrix= self.tf_matrix.A
    def setGeneratedDictionary(self):
        for _id , _word in enumerate(self.feature_names) :
            self.generatedDictionary[_word]=[]
            _columnOccurance=self.incidenceMatrix[:,_id]
            self.collectionStats["termCollectionFrenquency"].append({_word:sum(_columnOccurance)})
            for _idOccurence , _docNBR in enumerate(_columnOccurance):
                if _docNBR !=0 :
                    _list=self.generatedDictionary[_word]
                    _list.append("fr:{} -- D{} -- termeLength : {}".format(_docNBR,_idOccurence,len(_word)))
                    self.generatedDictionary[_word]=_list

    def documentStatistic(self):

        barWidth = 0.25
        # set height of bar
        bars1 = [x["DocumentLength"] for x in self.collectionStats["documentLenghtStats"]]
        
        # Set position of bar on X axis
        r1 = numpy.arange(len(self.collectionStats["documentLenghtStats"]))

        # Make the plot
        # pyplot.Line2D(r1, bars1, color='#00ff00', width=barWidth,
        #         edgecolor='white')
        
        pyplot.figure()# début de la figure5  plt.plot(X, Y)
        # Add xticks on the middle of the group bars
        # pyplot.xlabel('Documents ID', fontweight='bold')
        # pyplot.ylabel('Length', fontweight='bold')
        # pyplot.xticks([r  for r in range(len(bars1))], [x["DocumentId"] for x in self.collectionStats["documentLenghtStats"]])
        # # Create legend & Show graphic
        # pyplot.legend()
        pyplot.plot([x["DocumentId"] for x in self.collectionStats["documentLenghtStats"]],bars1)
        pyplot.show()

    def run(self):
        
        
        start_time=time.time()
        self.setListDocument()
        # self.setMatrixIncidence()
        # self.setGeneratedDictionary()
        self.documentStatistic()
        # print("Generated Collection :")
        # print(self.generatedDictionary)
        # print("\n Collection Statisques :")
        # print(self.collectionStats)
        # print(time.time() - start_time)

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