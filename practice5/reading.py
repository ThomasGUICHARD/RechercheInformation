from timing import logger
import re
from typing import List, Tuple, Generator, TextIO
from io import TextIOWrapper
import os
import os.path
import gzip
import zipfile
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
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

def getXmlTextSubSections(dataDirectory):
    _xmlDocs = os.listdir("{}".format(dataDirectory[0]))    
    # ./Practice_05_data/XML-Coll-withSem/
    for _xmlDoc in _xmlDocs :
        _docno= _xmlDoc.split(".")[0]
        
        _f=open("{}{}".format(dataDirectory[0],_xmlDoc))
        _str=_f.read()
        _doc=BeautifulSoup(_str,features="lxml")
        
        try:
            yield "{}/article[1]/header/title".format(_docno) , _doc.find("title").text
        except :
            pass
        
        try:
            yield "{}/article[1]/header/id".format(_docno) , _doc.find("id").text
        except :
            pass
        try:
            yield "{}/article[1]/header/revision".format(_docno),_doc.find("revision").text
        except :
            pass
        
        try:
            yield "{}/article[1]/header/categories".format(_docno),_doc.find("categories").text
        except :
            pass
        
        try:
            yield "{}/article[1]/header/contributor".format(_docno),_doc.find("contributor").text
           
        except :
            pass
        
        

        try:
            yield "{}/article[1]/header/timestamp".format(_docno),_doc.find("timestamp").text
            
        except :
            pass
        try:
            yield "{}/article[1]/header/username".format(_docno),_doc.find("username").text
         
        except :
            pass
        
        
        
        try:
            yield "{}/article[1]/bdy".format(_docno),_doc.find("bdy").text
        except :
            pass
        _f.close()

def getXmlText(dataDirectory):
    _xmlDocs = os.listdir("{}".format(dataDirectory[0]))    
    # ./Practice_05_data/XML-Coll-withSem/
    for _xmlDoc in _xmlDocs :
        print("[Reading {} file]".format(_xmlDoc))
        _f=open("{}{}".format(dataDirectory[0],_xmlDoc))
        _f=_f.read()
        # _f=_f.replace("&","")
        # t = ET.fromstring(_f)
        # _xmlText=''.join(t.findall('.//header')[0].itertext())+''.join(t.findall('.//bdy')[0].itertext())
        _xmlText=BeautifulSoup(_f,features="lxml").text
        _docno= _xmlDoc.split(".")
        yield  _docno[0],_xmlText.strip() 
         

def supply_docs(file_names: List[str]) -> Generator[Tuple[str, str], None, None]:
    """
    generate the tuple docno,text for each document in the files of file_names
    """
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
