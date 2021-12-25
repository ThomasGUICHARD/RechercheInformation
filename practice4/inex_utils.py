
from typing import Set, Generator, Tuple, TypeVar

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


def overlapp(s: Set[str], path: str) -> bool:
    """
    say if the path overlapp with another in the set
    """
    for p in xml_subpath_of(path):
        if p in s:
            return True

    return False


def remove_overlapping(generator: Generator[Tuple[T, str], None, None]) -> Generator[Tuple[T, str], None, None]:
    """
    filter all (t, path) with path overlapping with each other (first stay)
    """
    paths = set()
    for t, path in generator:
        if not overlapp(paths, path):
            yield t, path
            paths.add(path)
