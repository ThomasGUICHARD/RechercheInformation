
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
# txt is simply the a string with your XML file
_f=open("./Practice_05_data/XML-Coll-withSem/612.xml")
_f=_f.read()
# _f=_f.replace("&","")
ee=BeautifulSoup(_f,features="lxml")

# print(str(body.text))
print(ee.text)
