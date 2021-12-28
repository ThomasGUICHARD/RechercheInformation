from enum import Enum
from typing import List, Set, TextIO, Tuple
from algorithms import Algorithms
from index import porter_stemmer, stop_words, RankedRetrivialAnswer, IndexStore
from timing import logger
from itertools import islice
from inex_utils import remove_overlapping, remove_interleaved

# maximum line count per file
MAX_LINES = 10_500

DEFAULT_QUERIES = [
    ("2009011", "olive oil health benefit"),
    ("2009036", "notting hill film actors"),
    ("2009067", "probabilistic models in information retrieval"),
    ("2009073", "web link network analysis"),
    ("2009074", "web ranking scoring algorithm"),
    ("2009078", "supervised machine learning algorithm"),
    ("2009085", "operating system +mutual +exclusion")
]

DEFAULT_BM25_K = 1.2
DEFAULT_BM25_B = 0.75


class Granularity(Enum):
    ARTICLE = "articles"
    ELEMENTS = "elements"
    PASSAGES = "passages"


GRANULARITY_MAP = {}
# article[1]/bdy[1]/sec[3]/p[3]
GRANULARITY_MAP[Granularity.ARTICLE.value] = ["article"]
GRANULARITY_MAP[Granularity.ELEMENTS.value] = ["article", "bdy", "sec"]
GRANULARITY_MAP[Granularity.PASSAGES.value] = ["article", "bdy", "sec", "p"]
GRANU_LIST = [granu.value for granu in Granularity]


class Stop(Enum):
    NO_STOP = "nostop"
    STOP = "stop"


class Stem(Enum):
    NO_STEM = ("nostem", None)
    PORTER = ("porter", porter_stemmer)


class RunResultLine:
    def __init__(self, qid: str, file_name: str, rank: float, document_score: float, tag: str, path: str) -> None:
        self.qid = qid
        self.file_name = file_name
        self.rank = rank
        self.document_score = document_score
        self.tag = tag
        self.path = path

    def write(self, f: TextIO) -> None:
        # <qid> Q0 <article> <rank> <rsv> <run_id> <xml_path>
        f.write(
            f"{self.qid} Q0 {self.file_name} {self.rank} {self.document_score} {self.tag} {self.path}\n")


class RunResultProducer:
    def __init__(self, team_name: str) -> None:
        self.team_name = team_name
        self.base_id = 0

    def produce_result(self, index: IndexStore, algo: Algorithms, granularity: Granularity, stop: Stop, stem: Stem, queries: List[Tuple[str, str]] = None, bm25_k: float = DEFAULT_BM25_K, bm25_b: float = DEFAULT_BM25_B, stop_set: Set[str] = None, articles: int = 1500, apply_stemmer: bool = True, apply_stop_words: bool = True) -> None:
        """
        produce_result into a file, this method will update the store, if queries = None, DEFAULT_QUERIES is used
        """

        # get run uid
        run_id = self.base_id
        self.base_id += 1

        # set queries
        if queries == None:
            queries = DEFAULT_QUERIES

        if len(queries) * articles > MAX_LINES:
            raise Exception("|queries| * articles > MAX_LINES")

        # stop words part
        if stop == Stop.NO_STOP:
            stop_fn = stop.value
        else:
            if stop_set == None:
                stop_set = stop_words
            stop_fn = f"{stop.value}{len(stop_set)}"

        # write param for each algos
        if algo == Algorithms.ALGO_BM25:
            params = f"_k{bm25_k}_b{bm25_b}"
        else:
            params = ""

        # fetch stemmer
        stemmer_name, stemmer = stem.value

        # TeamName_Run-Id_WeigthingFunction_Granularity_Stop_Stem_Parameters.txt
        file_name = f"runs/{self.team_name}_{run_id}_{algo.value}_{granularity.value}_{stop_fn}_{stemmer_name}{params}.txt"

        logger.start()
        logger.write(f"Starting file {file_name}...")

        # prepare store
        if stop != Stop.NO_STOP and apply_stop_words:
            index.remove_stopwords(stop_set)

        if stem != Stem.NO_STEM and apply_stemmer:
            index.apply_stemmer(stemmer)

        if algo == Algorithms.ALGO_BM25:
            index.compute_bm25(bm25_k, bm25_b)
        elif algo == Algorithms.ALGO_LTC:
            index.compute_smart_ltc()
        elif algo == Algorithms.ALGO_LTN:
            index.compute_smart_ltn()
        else:
            raise Exception(f"Can't use {algo.value} to create run")

        results: List[RunResultLine] = []

        # parse queries
        for i, (qid, query) in enumerate(queries):
            logger.write(f"({i}) {qid} '{query}'")

            answers = index.compute_ranked_retrieval_as_list(query)
            answers = remove_overlapping(answers)
            answers = remove_interleaved(answers)

            # parse answers
            for rank, answer in enumerate(islice(answers, articles)):
                results.append(RunResultLine(qid, answer.doc,
                               rank, answer.wtdsum, self.team_name, answer.path))

        logger.write("Writing file...")
        logger.write("")
        with open(file_name, "w") as f:
            for i, result in enumerate(results):
                logger.write_no_endl(f"line {i}...")
                result.write(f)

        logger.write(f"Completed {file_name}...")

        logger.end()
