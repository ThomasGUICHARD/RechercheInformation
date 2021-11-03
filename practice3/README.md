# Recherche d'information

```
Usage: python main.py (filename+)

Options:
  -h, --help            show this help message and exit
  -s, --stemmer         apply stemmer
  -w, --stopwords       remove stopwords
  -q, --query           open query mode
  -i, --index           show index
  -o OUTPUT_DIR, --output_dir=OUTPUT_DIR
                        data output dir
  -S STEP, --step=STEP  step for stats
  -a ALGO, --algorithm=ALGO
                        algorithm to use to enter query mode, values: bool
                        bm25 ltc ltn
  -B BM25B, --bm25b=0.75
                        value of b if --algorithm=bm25
  -K BM25K1, --bm25k1=1.2
                        value of k1 if --algorithm=bm25
```

## Compute algorithm

You can compute 4 algorithms to query: bool (default) bm25 ltc ltn using the -a argument

```bash
python main.py FILES -a ALGORITHM
```

To select the $k_1$ or the $b$ argument for the BM25 algorithm, you can use the -B and -K argument

```bash
python main.py FILES -a bm25 -B 0.75 -K 1.2
```

## Query mode

To open the query mode, add -q in the argument, the query mode will ask for a query and answer the 10 best
answers or 10 answers if algo = bool

```
> web ranking scoring algorithm
4114 element(s) in 0.0s
- 23724 (5.631268237150827)
- 18336216 (5.090279872425114)
- 207747 (4.938184894135491)
- 2086074 (4.837464452070908)
- 6082436 (4.808593435787046)
- 15116785 (4.803006846802702)
- 1803281 (4.759158233376921)
- 6415715 (4.680669011661157)
- 5018563 (4.59750547376847)
- 10535584 (4.597065554644773)
```
