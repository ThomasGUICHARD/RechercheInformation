import re
from typing import Tuple, Generator
from sys import argv
from os import listdir
from os.path import isfile, join
import time
if len(argv) < 2:
    print(argv[0], "(filename)")
    exit(-1)

# %%
doc_read_pattern = re.compile("<doc><docno>([^<]*)</docno>([^<]*)</doc>")
doc_read_pattern_1 = re.compile("([^<]*)</doc>")
doc_read_pattern_2 = re.compile("([^<]*)")
doc_read_pattern_id = re.compile("<docno>([^<]*)</docno>")

def read_doc_id(text: str) -> str:
    matcher = doc_read_pattern_id.search(text)
    if matcher == None:
        return None
    return matcher.group(1)

def read_doc(text: str) -> str:
    matcher = doc_read_pattern.search(text)
    if matcher == None:
        matcher = doc_read_pattern_1.search(text)
        if matcher == None:
            matcher = doc_read_pattern_2.search(text)
            if matcher == None:
                return None
            return matcher.group(1)
            return None
        return matcher.group(1)
        return None
    return matcher.group(2)


supply_docs_doc_read_pattern = re.compile("<doc><docno>([^<]*)</docno>")
supply_docs_doc_read_end_pattern = re.compile("</doc>")

def supply_docs(file_name: str) -> Generator[Tuple[str, str], None, None]:
    with open(file_name) as f:
        while True: 
            line = f.readline()
            if line == '':
                break
            match = supply_docs_doc_read_pattern.search(line)
            if not match:
                continue

            docno = match.group(1)
            line = line[match.end():]
            text = ""
            while True:
                match = supply_docs_doc_read_end_pattern.search(line)
                if match:
                    text += line[:match.start()]
                    yield docno, text
                    break
                else:
                    text += line

                line = f.readline()
                if line == '':
                    break

# %%

fList = [f for f in listdir(argv[1]) if isfile(join(argv[1], f))]


# %%

class IndexObject:
    def __init__(self, size: int) -> None:
        self.df = 0
        self.tf = [0 for _ in range(size)] #ERREUR ICI au niveau de size qui est le nb ligne et pas le nbdoc
        #range(size)0 for _ in range(100000)


class IndexStore:
    def __init__(self, size: int) -> None:
        self.corpus_ids = dict()
        self.corpus_name_ids = []
        self.objects = dict()
        self.size = size

    def locate_docid(self, docid: str) -> int:
        oid = len(self.corpus_name_ids)
        self.corpus_ids[docid] = oid
        self.corpus_name_ids.append(docid)
        return oid

    def fetch_or_create_object(self, word: str) -> IndexObject:
        if word in self.objects:
            return self.objects[word]
        wl = IndexObject(self.size)
        self.objects[word] = wl
        return wl

    def tf_doc_of_object(self, word: str) -> Generator[Tuple[int, str], None, None]:
        if word not in self.objects:
            return

        tf = self.objects[word].tf

        for i in range(len(tf)):
            if tf[i] != 0:
                yield tf[i], self.corpus_name_ids[i]


#for f in fList:
start = time.process_time()
#t = [0 for _ in range(3)]
for i in range(0,1,1):#len(fList)
    start = time.process_time()
    f=fList[i]
    print(join(argv[1], f))
    with open(join(argv[1], f), "r") as myRepo:
        lines = myRepo.readlines()
    # %%

    index = IndexStore(len(lines))

    # Building index
    docnotmp=0

    for j in range(len(lines)):
        line = lines[j]
        doctext = read_doc(line)

        docno = docnotmp
        if read_doc_id(line) != None :
            docno = read_doc_id(line)


        ##print(docno==docnotmp)


       # print("doooooooooooooooooocnnnnnoobissssss{0}".format(docnobis))
        #print("doooooooooooooooooocnnnnnoo{0}".format(docno))
        docnotmp = docno
        docno = index.locate_docid(docno)

        if doctext != None:

            words = re.findall('\w+', doctext)
            for w in words:
                word = w.lower()

                wl = index.fetch_or_create_object(word)
                wl.df += 1
                wl.tf[docno] += 1
    end = time.process_time()
    print(end - start)
    #t[i-1] =end - start

#print(t)
# %%
"""
for word in sorted(index.objects):
    io = index.objects[word]
    print("{0}=df({1})".format(io.df, word))
    for tf, doc in index.tf_doc_of_object(word):
        print("\t{0} {1}".format(tf, str(doc)))
"""