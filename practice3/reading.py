from timing import logger
import re
from typing import List, Tuple, Generator, TextIO
from io import TextIOWrapper
import os
import os.path
import gzip
import zipfile

supply_docs_doc_read_pattern = re.compile("<doc><docno>([^<]*)</docno>")
supply_docs_doc_read_end_pattern = re.compile("</doc>")


def open_doc(file_name: str, *args, **kwargs) -> Generator[Tuple[TextIO, str], None, None]:
    fnl = file_name.lower()
    if fnl.endswith(".gz"):
        yield TextIOWrapper(gzip.open(file_name, "rb"), *args, **kwargs), os.path.basename(file_name)
    if fnl.endswith(".zip"):
        with zipfile.ZipFile(file_name) as archive:
            for f in archive.namelist():
                yield TextIOWrapper(archive.open(f), *args, **kwargs), os.path.join(os.path.basename(file_name), f)
    else:
        yield TextIOWrapper(open(file_name, "rb"), *args, **kwargs), os.path.basename(file_name)


def supply_files(file_names: List[str]) -> Generator[str, None, None]:
    for file_name in file_names:
        if os.path.isdir(file_name):
            for f in supply_files([os.path.join(file_name, f) for f in os.listdir(file_name)]):
                yield f
        else:
            yield file_name


def supply_docs(file_names: List[str]) -> Generator[Tuple[str, str], None, None]:
    for file_name in supply_files(file_names):
        # Open the file
        for iofile, rfile_name in open_doc(file_name, encoding="utf8"):
            logger.write(
                "Reading " + rfile_name + "...")
            with iofile as f:
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
