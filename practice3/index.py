from nltk.stem import PorterStemmer
from typing import List, Set, Tuple, Generator, Dict
from timing import logger

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
porter_stemmer = PorterStemmer()


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

    def merge_with(self, index2: 'IndexObject') -> None:
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
