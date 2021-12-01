from enum import Enum
from typing import Set
from algorithms import Algorithms
from index import porter_stemmer, stop_words, RankedRetrivialAnswer


class Granularity(Enum):
    ARTICLE = "articles"
    ELEMENTS = "elements"
    PASSAGES = "passages"


class Stop(Enum):
    NO_STOP = "nostop"
    STOP = "stop"


class Stem(Enum):
    NO_STEM = ("nostem", None)
    PORTER = ("porter", porter_stemmer)


class RunResultProducer:
    def __init__(self, team_name: str) -> None:
        self.team_name = team_name
        self.base_id = 0

    def produce_result(self, algo: Algorithms, granularity: Granularity, stop: Stop, stem: Stem, bm25_k: float = 1.2, bm25_b: float = 0.75, stop_set: Set[str] = None) -> None:
        # get run uid
        run_id = self.base_id
        self.base_id += 1

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
        file_name = f"{self.team_name}_{run_id}_{algo.value}_{granularity.value}_{stop_fn}_{stemmer_name}{params}.txt"
