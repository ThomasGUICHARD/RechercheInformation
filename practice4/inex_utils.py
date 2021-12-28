
from typing import List, Set, Generator, Tuple, TypeVar

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
    paths = set()
    spaths = set()
    for answer in lst:
        path = answer.path
        if not overlapp(paths, spaths, path):
            yield answer
            paths.add(path)
            for p in xml_subpath_of(path):
                spaths.add(p)


def remove_interleaved(lst: List[RankedRetrivialAnswer]) -> Generator[RankedRetrivialAnswer, None, None]:
    """
    remove the interleaved values
    """
    # TODO: remove interleaved
    return (e for e in lst)
