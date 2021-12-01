
from enum import Enum


class Algorithms(Enum):
    ALGO_ALL = "all"
    ALGO_BOOL = "bool"
    ALGO_BM25 = "bm25"
    ALGO_LTC = "ltc"
    ALGO_LTN = "ltn"


ALGO_LIST = [algo.value for algo in Algorithms]
