from nltk.stem import PorterStemmer
import re
from typing import List
from sys import argv
from timing import logger
from index import IndexStore
from reading import supply_docs


def main(argv: List[str]):
    if len(argv) < 2:
        print(argv[0], "(filename+)")
        return

    # locate end parenthesis of boolean expression

    index = IndexStore()

    # Building index

    logger.start()
    logger.write("Starting...")

    doc_count = 0
    word_count = 0

    for docno, doctext in supply_docs(argv[1:]):
        doc_count += 1
        words = re.findall('\w+', doctext)
        for w in words:
            word = w.lower()

            word_count += 1

            wl = index.fetch_or_create_object(word)
            wl.add_find(docno)

    # P3 - Delete stop words
    index.remove_stopwords()
    # P4 - Stemmer
    index.apply_stemmer()

    logger.write("Completed...")
    logger.end()

    print("Indexing time:   ", logger.get_time(), "s", sep="")
    print("Doc count:       ", doc_count, " doc(s)", sep="")
    print("Word count:      ", word_count, " word(s)", sep="")
    print("Vocabulary size: ", len(index.objects), " word(s)", sep="")

    if doc_count <= 10:
        for word in sorted(index.objects):
            io = index.objects[word]
            print("{0}=df({1})".format(io.df, word))
            for tf, doc in index.tf_doc_of_object(word):
                print("\t{0} {1}".format(tf, doc))
    else:
        print("List avoided because doc count > 10")


if __name__ == "__main__":
    main(argv)
