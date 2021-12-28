from run_result import Granularity, GRANULARITY_MAP
from timing import logger
import re
from typing import List, Tuple, Generator, TextIO
from io import TextIOWrapper
import os
import os.path
import gzip
import zipfile

from bs4 import BeautifulSoup
from bs4.element import Tag

supply_docs_doc_read_pattern = re.compile("<doc><docno>([^<]*)</docno>")
supply_docs_doc_read_end_pattern = re.compile("</doc>")


def open_doc(file_name: str, *args, **kwargs) -> Generator[Tuple[TextIO, str], None, None]:
    """
    generate TextIO and a file description for each files in file_name, can read .gz .zip or 
    text file, the arguments are the same as TextIOWrapper except the file_name
    """
    fnl = file_name.lower()

    if fnl.endswith(".gz"):  # .gz file
        yield TextIOWrapper(gzip.open(file_name, "rb"), *args, **kwargs), os.path.basename(file_name)
    if fnl.endswith(".zip"):  # .zip file
        with zipfile.ZipFile(file_name) as archive:
            for f in archive.namelist():
                yield TextIOWrapper(archive.open(f), *args, **kwargs), os.path.join(os.path.basename(file_name), f)
    else:  # Read all the other files as text file
        yield TextIOWrapper(open(file_name, "rb"), *args, **kwargs), os.path.basename(file_name)


def supply_files(file_names: List[str]) -> Generator[str, None, None]:
    """
    search and generate all the file_names for a particular name
    """
    for file_name in file_names:
        if os.path.isdir(file_name):
            # Is dir? fetch the sub files
            for f in supply_files([os.path.join(file_name, f) for f in os.listdir(file_name)]):
                yield f
        else:
            yield file_name


def name_no_ext(file: str) -> str:
    """
    get the basename of a file without the extension
    """
    bn = os.path.basename(file)
    try:
        return bn[:(len(bn) - 1 - bn[::-1].index("."))]
    except ValueError:
        return bn


def recursive_supply(docno: str, path: str, root: Tag, nodes: List[str]) -> Generator[Tuple[str, str], None, None]:
    """
    recursively find the sub tag of a node
    """

    for index, tag in enumerate(root.find_all(nodes[0])):
        # append the new node to the path
        npath = f"{path}/{nodes[0]}[{(index + 1)}]"

        # get the text
        doctext = tag.get_text()

        # get the docno for this doc+path
        ndocno = docno + ":" + npath

        # send it to parsing
        yield ndocno, doctext

        # check if we have to find new tags
        if len(nodes) == 1:
            return

        # yield future results recursively
        for e in recursive_supply(docno, npath, tag, nodes[1:]):
            yield e


def supply_docs(file_names: List[str], granu: Granularity) -> Generator[Tuple[str, str], None, None]:
    """
    generate the tuple docno,text for each document in the files of file_names
    """
    nodes = GRANULARITY_MAP[granu.value]
    for file_name in supply_files(file_names):
        # Open the file
        for iofile, rfile_name in open_doc(file_name, encoding="utf8"):
            logger.write_no_endl(
                "Reading " + rfile_name + "...")
            docno = name_no_ext(rfile_name)
            with iofile as f:
                soup = BeautifulSoup("\n".join(f.readlines()), "xml")
                for docno, doctext in recursive_supply(docno, "", soup, nodes):
                    yield docno, doctext
    logger.write("")
    logger.write("Reading completed")
