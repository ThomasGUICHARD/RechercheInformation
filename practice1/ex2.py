# %%
import re
from typing import Tuple, Generator
from sys import argv

if len(argv) < 2:
    print(argv[0], "(filename)")
    exit(-1)


# %%
doc_read_pattern = re.compile("<doc><docno>([^<]*)</docno>([^<]*)</doc>")


def read_doc(text: str) -> Tuple[str, str]:
    matcher = doc_read_pattern.search(text)
    if matcher == None:
        return None, None
    return matcher.group(1), matcher.group(2)


# %%
with open(argv[1], "r") as f:
    lines = f.readlines()


# %%

class IndexObject:
    def __init__(self, size: int) -> None:
        self.df = 0
        self.tf = [0 for _ in range(size)]


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


# %%
index = IndexStore(len(lines))

# Building index

for i in range(len(lines)):
    line = lines[i]
    docno, doctext = read_doc(line)
    if docno == None:
        continue
    docno = index.locate_docid(docno)

    words = re.findall('\w+', doctext)
    for w in words:
        word = w.lower()

        wl = index.fetch_or_create_object(word)
        wl.df += 1
        wl.tf[docno] = 1


# %%
for word in sorted(index.objects):
    io = index.objects[word]
    print("{0}=df({1})".format(io.df, word))
    for tf, doc in index.tf_doc_of_object(word):
        print("\t{0} {1}".format(tf, doc))


# %%
