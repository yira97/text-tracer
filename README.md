# text-tracer
a text-searching script base on **bayesian network** and **word2vec**

1. ~~c++11~~
2. python3
## install
### 1. get the latest version of wiki dumpfile
    $ curl https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2  
    $ 7z e enwiki-latest-pages-articles.xml.bz2
### 2. parse the origin xml using [wikiextractor](https://github.com/attardi/wikiextractor)
    
    $ git clone https://github.com/attardi/wikiextractor && cd wikiextractor
    $ python3 setup.py install
    $ python3 --html -s WikiExtractor.py
### 3. build graph
    $ cd .. && git clone https://github.com/ethanmiles/Bayesian-Network-for-NLP && cd Bayesian-Network-for-NLP
    $ python3 xmlParser.py  --input x --work x -p

### 4. start searching! 
    $ python3 xmlParser.py  --work x -q feedback
## dev schedule
### 1. corpus processing
xml_parser.hpp contains a series of xml processing tools which can basically cover various requirement of student or scholar.

Method Preview:
* [x] split tags 
---
### 2. bayesian graph construction
* [x] edges
* [x] nodes
* [x] probabilistic table
* [x] tfidf
* [x] bayesian network inference
---
### 3. advance application
* [x] building graph from structured documents
---
## 4. test
* [x] graph_test
* [x] xml_parser_test
