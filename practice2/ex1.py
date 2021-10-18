from nltk.stem import PorterStemmer
import re
from typing import List, Set, Tuple, Generator, Dict, TextIO
from sys import argv
import os
import os.path
from timing import TimingWriting
import gzip

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
porter_stemmer = PorterStemmer()

if len(argv) < 2:
    print(argv[0], "(filename+)")
    exit(-1)

logger = TimingWriting()

supply_docs_doc_read_pattern = re.compile("<doc><docno>([^<]*)</docno>")
supply_docs_doc_read_end_pattern = re.compile("</doc>")


def open_doc(file_name: str, *args, **kwargs) -> TextIO:
    if file_name.lower().endswith(".gz"):
        return gzip.open(file_name, *args, **kwargs)
    else:
        return open(file_name, *args, **kwargs)


def supply_files(file_names: List[str]) -> Generator[str, None, None]:
    for file_name in file_names:
        if os.path.isdir(file_name):
            for f in supply_files([os.path.join(file_name, f) for f in os.listdir(file_name)]):
                yield f
        else:
            yield file_name


def supply_docs(file_names: List[str]) -> Generator[Tuple[str, str], None, None]:
    for file_name in supply_files(file_names):
        logger.write("Reading " + os.path.basename(file_name) + "...")
        # Open the file
        with open_doc(file_name, "rt", encoding="utf8") as f:
            while True:
                # EOF?
                line = f.readline()
                if line == '':
                    break

                # Read doc no
                match = supply_docs_doc_read_pattern.search(line)
                if not match:
                    continue  # or pass if error

                docno = match.group(1)
                line = line[match.end():]
                text = ""
                while True:
                    # contain end of doc?
                    match = supply_docs_doc_read_end_pattern.search(line)
                    if match:
                        # yield the docno and the text
                        text += line[:match.start()]
                        yield docno, text
                        break
                    else:
                        text += line

                    line = f.readline()
                    if line == '':  # pass if the doc isn't ended but the the file is
                        break
    logger.write("Reading completed")

# locate end parenthesis of boolean expression


def locate_end_parenthesis(exp: List[str], start: int) -> int:
    deep = 0
    for i in range(start, len(exp)):
        c = exp[i]
        if c == '(':
            deep += 1
        elif c == ')':
            if deep == 0:
                return i
            else:
                deep -= 1
    raise Exception("No end parenthesis!")


def and_lst(a: Set[str], b: Set[str], not_b: bool) -> None:
    """
    equivalent to a &= b
    """
    if not_b:
        raise Exception("'not' not implemented")

    a = a.intersection(b)


def or_lst(a: Set[str], b: Set[str], not_b: bool) -> None:
    """
    equivalent to a |= b
    """
    if not_b:
        raise Exception("'not' not implemented")

    a = a.union(b)


class IndexObject:
    def __init__(self) -> None:
        self.df = 0
        self.tf = dict()

    def add_find(self, doc) -> None:
        self.df += 1
        if doc in self.tf:
            self.tf[doc] += 1
        else:
            self.tf[doc] = 1

    def merge_with(self, index2) -> None:
        self.df += index2.df
        for doc in index2.tf:
            if doc in self.tf:
                self.tf[doc] += index2.tf[doc]
            else:
                self.tf[doc] = index2.tf[doc]


class IndexStore:
    def __init__(self) -> None:
        self.corpus_ids = dict()
        self.corpus_name_ids = []
        self.objects = dict()

    def fetch_or_create_object(self, word: str) -> IndexObject:
        if word in self.objects:
            return self.objects[word]
        wl = IndexObject()
        self.objects[word] = wl
        return wl

    def tf_doc_of_object(self, word: str) -> Generator[Tuple[int, str], None, None]:
        if word not in self.objects:
            return

        tf = self.objects[word].tf

        for doc in tf:
            yield tf[doc], doc

    def fetch_word_tf(self, word: str) -> Dict[str, int]:
        if word in self.objects:
            return self.objects[word].tf
        return dict()

    def remove_stopwords(self):
        logger.write("Removing stopwords...")
        for word in stop_words:
            if word in self.objects:
                del self.objects[word]

    def apply_stemmer(self):
        logger.write("Applying stemmer...")

        # TODO: duplicate the size of the heap, find a better way
        future_objects = dict()

        for word in self.objects:
            obj = self.objects[word]
            w = porter_stemmer.stem(word)

            if w in future_objects:
                future_objects[w].merge_with(obj)
            else:
                future_objects[w] = obj

        self.objects = future_objects

    def parse_expr(self, exp: List[str]) -> Set[str]:
        and_result = set()

        i = 0
        next_inverted = False
        while i < len(exp):
            op = exp[i]
            i += 1

            if op == "!":
                next_inverted = True
                continue

            if op == "":
                continue

            if op == "(":
                end = locate_end_parenthesis(exp, i)
                output = self.parse_expr(exp[i:end])
                and_lst(and_result, output, next_inverted)
                i = end + 1
            elif op == "|":
                b = self.parse_expr(exp[i:len(exp)])
                or_lst(and_result, b, next_inverted)
                return and_result
            else:
                # word
                and_lst(and_result, self.fetch_word_tf(op), next_inverted)
            next_inverted = False

        return and_result

    def parse(self, exp: str) -> Generator[str, None, None]:
        result = self.parse_expr(exp.lower().split(" "))

        for i in range(len(result)):
            if result[i] != 0:
                yield self.corpus_name_ids[i]


index = IndexStore()

# Building index

logger.start()

doc_count = 0
word_count = 0

for docno, doctext in supply_docs(argv[1:]):
    doc_count += 1
    words = re.findall('\w+', doctext)
    for w in words:
        word = w.lower()

        word_count += 1

        wl = index.fetch_or_create_object(word)
        wl.add_find(docno)

# P3 - Delete stop words
index.remove_stopwords()
# P4 - Stemmer
index.apply_stemmer()

logger.end()

print("Indexing time:   ", logger.get_time(), "s", sep="")
print("Doc count:       ", doc_count, " doc(s)", sep="")
print("Word count:      ", word_count, " word(s)", sep="")
print("Vocabulary size: ", len(index.objects), " word(s)", sep="")


if doc_count <= 10:
    for word in sorted(index.objects):
        io = index.objects[word]
        print("{0}=df({1})".format(io.df, word))
        for tf, doc in index.tf_doc_of_object(word):
            print("\t{0} {1}".format(tf, doc))
else:
    print("List avoided because doc count > 10")

# for doc in index.parse(" ".join(argv[2:])):
#     print("-", doc)
