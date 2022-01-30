
from typing import Dict, Iterator, List, Set, Generator, Tuple, TypeVar

from index import RankedRetrivialAnswer

T = TypeVar("T")


def xml_subpath_of(p: str) -> Generator[str, None, None]:
    """
    get all xml sub path of a path, example:
    "", "/article[1]", "/article[1]/bdy[1]", "/article[1]/bdy[1]/sec[2]"
    """
    try:
        i = -1
        while True:
            i = p.index("/", i + 1)
            yield p[:i]
    except ValueError:
        yield p


def overlapp(s: Set[str], s2: Set[str], path: str) -> bool:
    """
    say if the path overlapp with another in the set
    """
    if path in s2:
        return True

    for p in xml_subpath_of(path):
        if p in s:
            return True

    return False


def remove_overlapping(lst: List[RankedRetrivialAnswer]) -> Generator[RankedRetrivialAnswer, None, None]:
    """
    filter all (t, path) with path overlapping with each other (first stay)
    """
    paths = dict()

    for answer in lst:
        path = answer.path
        if answer.doc not in paths:
            paths[answer.doc] = (set(), set())

        dpaths, dspaths = paths[answer.doc]

        if not overlapp(dpaths, dspaths, path):
            yield answer
            dpaths.add(path)
            for p in xml_subpath_of(path):
                dspaths.add(p)


def remove_interleaved(it: Iterator[RankedRetrivialAnswer]) -> Generator[RankedRetrivialAnswer, None, None]:
    """
    remove the interleaved values
    """
    answers: List[List[RankedRetrivialAnswer]] = []
    doc_index: Dict[str, int] = dict()

    for answer in it:
        if answer.doc not in doc_index:
            doc_index[answer.doc] = len(answers)
            answers.append([answer])
        else:
            answers[doc_index[answer.doc]].append(answer)

    for doclist in answers:
        for asw in doclist:
            yield asw
