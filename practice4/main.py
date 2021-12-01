from os import stat
import re
from typing import List
from timing import logger, QuickTime
from index import IndexObject, IndexStore
from reading import supply_docs
from optparse import OptionParser, Values
import query_parser
import itertools
from run_result import Granularity, Stop, Stem, RunResultProducer
from algorithms import ALGO_LIST, Algorithms


def compute_algo(algo: Algorithms, index: IndexObject, options: Values):
    if algo == Algorithms.ALGO_ALL or algo == Algorithms.ALGO_BOOL:
        return

    logger.write("Computing algorithm " + algo.value)

    if algo == Algorithms.ALGO_LTN:
        index.compute_smart_ltn()
    elif algo == Algorithms.ALGO_LTC:
        index.compute_smart_ltc()
    elif algo == Algorithms.ALGO_BM25:
        index.compute_bm25(options.bm25k1, options.bm25b)

    logger.write(
        "test ranked retrieval... '" + options.algo_sentence + "'")
    answer = index.compute_ranked_retrieval_as_list(options.algo_sentence)
    # Print the answers
    for a in itertools.islice(answer, 10):
        print("-", a.doc, "(" + str(a.wtdsum) + ")")


def run_index(args: List[str]):
    index = IndexStore()

    # Number of document for this session
    doc_count = 0
    # Number of word for this session
    word_count = 0

    for docno, doctext in supply_docs(args):
        doc_count += 1
        # Fetch all the words
        words = re.findall('\w+', doctext)
        for w in words:
            word = w.lower()

            word_count += 1

            # Fetch an index object and add a find
            index.add_word(docno, word)

    return index, doc_count, word_count


def main():
    # Add options to the prog
    parser = OptionParser()

    parser.add_option("-s", "--stemmer", dest="stemmer", action="store_true",
                      help="apply stemmer", default=False)
    parser.add_option("-w", "--stopwords", dest="stopwords", action="store_true",
                      help="remove stopwords", default=False)
    parser.add_option("-q", "--query", dest="query", action="store_true",
                      help="open query mode", default=False)
    parser.add_option("-i", "--index", dest="index", action="store_true",
                      help="show index", default=False)
    parser.add_option("-o", "--output_dir", dest="output_dir",
                      help="data output dir", default="output_dir")
    parser.add_option("-S", "--step", dest="step", type="int",
                      help="step for stats", default=1000)

    parser.add_option("-a", "--algorithm", dest="algo",
                      help="algorithm to use to enter query mode, values: " + " ".join(ALGO_LIST), default=Algorithms.ALGO_ALL.value)
    parser.add_option("-A", "--algorithm_sentence", dest="algo_sentence",
                      help="algorithm try value", default="web ranking scoring algorithm")

    parser.add_option("-B", "--bm25b", dest="bm25b", type="float",
                      help="value of b if --algorithm=bm25", default=0.75)
    parser.add_option("-K", "--bm25k1", dest="bm25k1", type="float",
                      help="value of k1 if --algorithm=bm25", default=1.2)
    parser.add_option("-R", "--runs", dest="run", action="store_true",
                      help="show index", default=False)
    parser.set_usage(parser.get_prog_name() + " (filename+)")

    options, args = parser.parse_args()

    if len(args) < 1 or options.algo not in ALGO_LIST:
        parser.print_usage()
        return

    algo = Algorithms(options.algo)

    if options.run:
        producer = RunResultProducer("NassimAntoineThomasMelanie")
        logger.start()
        logger.write("Running index...")
        index, _, _ = run_index(args)
        logger.end()
        producer.produce_result(
            index, Algorithms.ALGO_LTC, Granularity.ARTICLE, Stop.NO_STOP, Stem.NO_STEM, apply_stemmer=False, apply_stop_words=False)
        producer.produce_result(
            index, Algorithms.ALGO_LTN, Granularity.ARTICLE, Stop.NO_STOP, Stem.NO_STEM, apply_stemmer=False, apply_stop_words=False)
        producer.produce_result(
            index, Algorithms.ALGO_BM25, Granularity.ARTICLE, Stop.NO_STOP, Stem.NO_STEM, apply_stemmer=False, apply_stop_words=False)

        producer.produce_result(
            index, Algorithms.ALGO_LTC, Granularity.ARTICLE, Stop.NO_STOP, Stem.PORTER, apply_stemmer=True, apply_stop_words=False)
        producer.produce_result(
            index, Algorithms.ALGO_LTN, Granularity.ARTICLE, Stop.NO_STOP, Stem.PORTER, apply_stemmer=False, apply_stop_words=False)
        producer.produce_result(
            index, Algorithms.ALGO_BM25, Granularity.ARTICLE, Stop.NO_STOP, Stem.PORTER, apply_stemmer=False, apply_stop_words=False)

        producer.produce_result(
            index, Algorithms.ALGO_LTC, Granularity.ARTICLE, Stop.STOP, Stem.PORTER, apply_stemmer=False, apply_stop_words=True)
        producer.produce_result(
            index, Algorithms.ALGO_LTN, Granularity.ARTICLE, Stop.STOP, Stem.PORTER, apply_stemmer=False, apply_stop_words=False)
        producer.produce_result(
            index, Algorithms.ALGO_BM25, Granularity.ARTICLE, Stop.STOP, Stem.PORTER, apply_stemmer=False, apply_stop_words=False)

        logger.start()
        logger.write("Running index...")
        index, _, _ = run_index(args)
        logger.end()

        producer.produce_result(
            index, Algorithms.ALGO_LTC, Granularity.ARTICLE, Stop.STOP, Stem.NO_STEM, apply_stemmer=False, apply_stop_words=True)
        producer.produce_result(
            index, Algorithms.ALGO_LTN, Granularity.ARTICLE, Stop.STOP, Stem.NO_STEM, apply_stemmer=False, apply_stop_words=False)
        producer.produce_result(
            index, Algorithms.ALGO_BM25, Granularity.ARTICLE, Stop.STOP, Stem.NO_STEM, apply_stemmer=False, apply_stop_words=False)
    else:
        # locate end parenthesis of boolean expression
        logger.start()
        logger.write("Starting...")

        index, doc_count, word_count = run_index(args)

        # P3 - Delete stop words
        if options.stopwords:
            index.remove_stopwords()

        # P4 - Stemmer
        if options.stemmer:
            index.apply_stemmer()

        # Practice 3 - wdf
        if algo == Algorithms.ALGO_ALL:
            for alg in Algorithms:
                compute_algo(alg, index, options)
        elif algo != Algorithms.ALGO_BOOL:
            compute_algo(algo, index, options)

        logger.write("Completed...")

        logger.end()

        print("Indexing time:   ", logger.get_time(), "s", sep="")
        print("Doc count:       ", doc_count, " doc(s)", sep="")
        print("Word count:      ", word_count, " word(s)", sep="")
        print("Vocabulary size: ", len(index.objects), " word(s)", sep="")

        # Print index if asked or not enough element
        if doc_count <= 10 or options.index:
            for word in sorted(index.objects):
                io = index.objects[word]
                print("{0}=df({1})".format(io.get_document_frequency(), word))
                for tf, doc in index.tf_doc_of_object(word):
                    print("\t{0} {1}".format(tf, doc))
        else:
            print("List avoided because doc count > 10")

        # (P4) Enter in query mode
        if options.query:
            timer = QuickTime()
            while True:
                query = input("> ")
                timer.start()
                if algo != Algorithms.ALGO_BOOL:
                    answer = [
                        a.doc + " (" + str(a.wtdsum) + ")" for a in index.compute_ranked_retrieval_as_list(query)]
                else:
                    answer = query_parser.parse(index, query)
                timer.end()
                print(len(answer), " element(s) in ",
                      timer.last_time(), "s", sep="")

                # Print the answers
                for a in itertools.islice(answer, 10):
                    print("-", a)


if __name__ == "__main__":
    main()
