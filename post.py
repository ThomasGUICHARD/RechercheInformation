from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
stop_words = ['<', '>', 'doc', '/doc', 'docno', '/docno', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9']

##Def of docCount
class WordByDocumentList:
    document = ""
    occurence = 0
    def __init__(self):
        self.size = 0
        self.word = ""
        self.docCount = []


##Def of word list
class DocCount:
    word = ""
    docCount = []
    size = 0

    def __init__(self, token):
        self.size = 0
        self.word = token
        self.docCount = []


##Def of posting list object
class  PostingList:
    size = 0

    def __init__(self):
        self.size=0
        print("il y en a maintenant ", self.size)

    @classmethod
    def get_nb(cls):
        return PostingList.size






##print(stop_words)

f = open('document/doc.txt', 'r')
docs = f.readlines()


"""tokenization"""
tf = CountVectorizer(stop_words=stop_words)
tf_matrix = tf.fit_transform(docs)


##print(tf_matrix)

##print(tf.get_feature_names())


##matrice token-document
##print(tf_matrix.A)


## return booblean from matrix
def column(matrix, i):
    return [row[i] for row in matrix]

## print postlist but do not register it
def makePostingList(tf_matrix):
    for i in range(21):
        count = len(column(tf_matrix.A, i)) - column(tf_matrix.A, i).count(0)
        print(count, "=df(", tf.get_feature_names()[i],")")
        for k in range (0,10):
            if tf_matrix.A[k,i] > 0:
                print(tf_matrix.A[k,i], " D", k, sep='')
        print(" ")


def intersection(list1, list2):
    list3 = [value for value in list1 if value in list2]
    return list3

def AND(x, y):
    list_x = []
    list_y = []
    for i in range(21):
        if x == tf.get_feature_names()[i]:
            col_bis = column(tf_matrix.A, i)
            count_bis = 0
            for i in col_bis:
                if i>0:
                    list_x.append(count_bis)
                count_bis = count_bis+1
        elif y == tf.get_feature_names()[i]:
            col_bis = column(tf_matrix.A, i)
            count_bis = 0
            for i in col_bis:
                if i>0:
                    list_y.append(count_bis)
                count_bis = count_bis+1
    print(intersection(list_x, list_y))
    
def OR(x, y):
    list_x = []
    list_y = []
    for i in range(21):
        if x == tf.get_feature_names()[i]:
            col_bis = column(tf_matrix.A, i)
            count_bis = 0
            for i in col_bis:
                if i>0:
                    list_x.append(count_bis)
                count_bis = count_bis+1
        elif y == tf.get_feature_names()[i]:
            col_bis = column(tf_matrix.A, i)
            count_bis = 0
            for i in col_bis:
                if i>0:
                    list_y.append(count_bis)
                count_bis = count_bis+1
    print(list_x + list(set(list_y)-set(list_x)))
    
def NOT(x, y):
    list_x = []
    list_y = []
    for i in range(21):
        if x == tf.get_feature_names()[i]:
            col_bis = column(tf_matrix.A, i)
            count_bis = 0
            for i in col_bis:
                if i>0:
                    list_x.append(count_bis)
                count_bis = count_bis+1
        elif y == tf.get_feature_names()[i]:
            col_bis = column(tf_matrix.A, i)
            count_bis = 0
            for i in col_bis:
                if i>0:
                    list_y.append(count_bis)
                count_bis = count_bis+1
    print(list(set(list_x)-set(list_y)))


makePostingList(tf_matrix)


AND('the', 'of')
OR('the', 'of')
NOT('the', 'of')
