# %%
from typing import List, Generator, Tuple
import re
from typing import Tuple, Generator
from sys import argv

if len(argv) < 3:
    print(argv[0], "(filename) (query)")
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


def and_lst(a: List[int], b: List[int], not_b: bool) -> None:
    """
    equivalent to a &= b
    """
    if not_b:
        for i in range(len(a)):
            a[i] &= 1 - b[i]
    else:
        for i in range(len(a)):
            a[i] &= b[i]


def or_lst(a: List[int], b: List[int], not_b: bool) -> None:
    """
    equivalent to a |= b
    """
    if not_b:
        for i in range(len(a)):
            a[i] |= 1 - b[i]
    else:
        for i in range(len(a)):
            a[i] |= b[i]


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

    def empty_arr(self) -> List[int]:
        return [0 for _ in range(self.size)]

    def fetch_word_tf(self, word: str) -> List[int]:
        if word in self.objects:
            return self.objects[word].tf
        return self.empty_arr()

    def parse_expr(self, exp: List[str]) -> List[int]:
        and_result = [1 for _ in range(self.size)]

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
for doc in index.parse(" ".join(argv[2:])):
    print("-", doc)
