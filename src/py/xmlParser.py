import re
import os
import sys
import argparse
import math
import heapq
from gensim.models import Word2Vec

# arguments config
parser = argparse.ArgumentParser(
    description="This is a document indexing engine using bayesian network.\nFor more information see https://github.com/ethanmiles/Bayesian-Network-for-NLP")
parser.add_argument('-i', '--input', type=str,
                    help='directory hold result of wikiextractor.', dest="input_path")
parser.add_argument('-o', '--work', type=str,
                    help='working directory.', dest="work_path")
parser.add_argument('-t', '--filter', type=str,
                    help='terminology filter text path')
parser.add_argument('-l', '--level', type=int,
                    help='max search deep of tag.', default=3)
group = parser.add_mutually_exclusive_group()
group.add_argument('-p', '--preprocess',
                   action='store_true', help='start process wikiextractor data and generate work data.')
group.add_argument('-q', '--query', nargs='+',
                   help='type in the words you want contained by document, split each words by space.')
args = parser.parse_args()




class Vertex:

    def __init__(self, level, text):
        self.level = level
        self.text = text
        self.children = []
        self.tf = {}  # term frequencies
        self.p = 0  # probability

    @staticmethod
    def Descendants(v, l):
        for c in v.children:
            Vertex.Descendants(c, l)
        l.append(v)

    @staticmethod
    def Vertexs(vs):
        l = []
        for v in vs:
            Vertex.Descendants(v, l)
        return l

    def getDescendants(self):
        l = []
        Vertex.Descendants(self, l)
        return l

    def getTF(self, term):
        if term not in self.tf:
            self.setTF(term)
        return self.tf[term]

    def setTF(self, term):
        self.tf[term] = len(re.findall(term, self.text))


class Graph:
    def __init__(self, workPath, maxLevel=3):
        self.workPath = workPath
        self.maxLevel = maxLevel
        # vertex number of the every layer
        self.layer = {i: 0 for i in range(self.maxLevel+1)}
        self.roots = []  # document's roots
        self.terms = {}  # {term: {level:count} }

        self.initRoots()
        self.initTerms()
        self.initLayer()
        self.initIDF()
        self.initTF()

    def initIDF(self):
        vs = Vertex.Vertexs(self.roots)
        for t in self.terms:
            for v in vs:
                if t in v.text:
                    self.terms[t][v.level] += 1
        for t in self.terms:
            for h in self.terms[t]:
                if self.terms[t][h] > 0:
                    self.terms[t][h] = math.log(
                        self.layer[h] / self.terms[t][h])

    def getIDF(self, termName, level):
        return self.terms[termName][level]

    def initTF(self):
        for v in Vertex.Vertexs(self.roots):
            if v.level == self.maxLevel:
                for t in self.getTerminologys():
                    v.setTF(t)
            else:
                pass  # vertex which doesn't direct connect with terminoloty do not have df

    def terminologyWeight(self, term, leaf):
        return leaf.getTF(term) * self.getIDF(term, self.maxLevel)

    def vertexWeight(self, leaf, trunk):  # 1/count(leaf's bro)
        for n in Vertex.Vertexs(self.roots):
            if leaf in n.children:
                return 1 / len(n.children)

    def getWeight(self, n1, n2):
        if n2.level == self.maxLevel:  # n1 is terminology
            return self.terminologyWeight(n1, n2)
        else:  # n1 is normal vertex
            return self.vertexWeight(n1, n2)

    def genScores(self, vs, min_return_score=50, short_penalty_limit=30):
        psum = 0
        pmax = 0
        for v in vs:
            # penalty for short text
            if len(v.text) < short_penalty_limit:
                v.p /= 2
            if v.p > pmax:
                pmax = v.p
            psum += v.p
        print("pmax: ",pmax,"\npsum: ",psum)
        for v in vs:
            v.p /= pmax
            v.p *= 100
        vs = [v for v in vs if v.p > min_return_score ] 
        return vs


    def search(self, queries):
        print("query before transform: ", queries)
        #queries = self.match(queries)
        print(" query after transform: ", queries)

        vs = Vertex.Vertexs(self.roots)
        # first process the leaf
        for n in vs:
            if n.level == self.maxLevel:
                n.p = 0
                for t in self.terms:
                    if t in queries:
                        n.p += self.getWeight(t, n)
                    else:
                        n.p += self.getWeight(t, n) / len(t)
        # process from second-end level to root level
        for i in range(self.maxLevel-1, 0, -1):
            for n in vs:
                if n.level == i:
                    for c in n.children:
                        n.p += (c.p * self.getWeight(c, n))

        

        vs = self.genScores(vs)
        return vs

    def initLayer(self):
        for v in Vertex.Vertexs(self.roots):
            self.layer[v.level] += 1

    def initTerms(self):
        for t in self.getTerminologys():
            self.terms[t] = {i: 0 for i in range(self.maxLevel+1)}

    def getTerminologys(self):
        terms = []
        stri = ""
        for i in range(1, self.maxLevel+1):
            stri += str(i)
        for f in allfilepaths(self.workPath):
            with open(f, "r", encoding="utf-8") as f_read:
                text = f_read.read()
                for t in re.findall(r"<h["+stri+r"]>(.*?)</h\d>", text):
                    terms.append(t)
        terms = [term.lower() for term in terms if len(term.split()) <= 1]
        terms = set(terms)
        with open("stopwords.txt", "r", encoding="utf-8") as f_read:
            stopwords = f_read.read()
            terms - set(stopwords.split())
        return terms

    def initRoots(self):
        for f in allfilepaths(self.workPath):
            with open(f, "r", encoding="utf-8") as f_read:
                text = f_read.read()
                self.roots.append(Graph.GenerateRoots(text, self.maxLevel))

    # [params] do not pass h paramerter.
    @staticmethod
    def GenerateRoots(text, maxLevel=4, h=1):
        if len(text) == 0:
            return
        stri = r"<h"+str(h)+r">.*?</h"+str(h) + \
            r">([\s\S]*?)(?=<h" + str(h)+r">(.*?)</h"+str(h)+r")"
        inners = re.findall(stri, text)

        if len(inners) > 0:
            strLast = r"<h"+str(h)+r">" + \
                inners[-1][-1]+r"</h"+str(h)+r">([\s\S]*)"
        else:
            strLast = r"<h"+str(h)+r">.*?</h"+str(h)+r">([\s\S]*)"
        last = re.findall(strLast, text)
        if len(last) > 0:
            inners.append((last[0], ""))
        children = []
        if len(inners) != 0:
            for i in inners:
                if (h <= maxLevel):
                    children.append(Graph.GenerateRoots(i[0], maxLevel, h+1))
        v = Vertex(h - 1, re.sub(r'<.*>', "", text))
        v.children = children
        return v

    def match(self, queries):
        MATCH_GAP = 0.00001
        queries = [q.lower() for q in queries]
        model = Word2Vec.load("word2vec.model")
        res = []
        for q in queries:
            try:
                alter_t = []
                max_sim = 0
                for t in self.terms:
                    sim = model.wv.similarity(q, t)
                    if sim > max_sim:
                        max_sim = sim
                for t in self.terms:
                    if model.wv.similarity(q, t) > max_sim - MATCH_GAP:
                        alter_t.append(t)
                for t in alter_t:
                    res.append(t)
            except KeyError as e:
                # ignore word if engine never see it before
                pass

        # stop search if no matchd
        if len(res) == 0:
            print("no result")
            exit(0)
        return res

# wikiStanderdize(inputFilePath, outputFilePath)


class wikiProcessor:
    def __init__(self, inputFilePath, outputFilePath):
        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath
        self.nameIndex = 1

    def run(self):
        self.wikiStanderdize()

    def wikiStanderdize(self):
        rule = [r"<doc>.*?<h1>.*?</h1>\n.*?may refer to[\s\S]*?</doc>", r"<h2>See also</h2>", r"<h2>References</h2>",
                r"<h3>Specific</h3>", r"<h3>General</h3>", r"<h2>External links</h2>"]

        for f in allfilepaths(self.inputFilePath):
            print("start process : ", f)
            self.standerdize(f, rule)

    def standerdize(self, f, extraRules, splitTag="doc"):

        with open(f, "r", encoding="utf-8") as f_read:
            text = f_read.read().lower()

        text = re.sub("<doc.*>", "<doc>", text)
        text = re.sub(r"<li>.*</li>", "", text)
        text = re.sub(r"<ul>[\s\S]*?</ul>", "", text)
        text = re.sub(r"<ol>[\s\S]*?</ol>", "", text)
        text = re.sub("</ul>", "", text)
        text = re.sub("&lt;/a&gt;", "", text)
        text = re.sub("&lt;a href=.*?&gt;", "", text)
        text = re.sub(r"\[.*\]", " ", text)
        text = re.sub(r"\(.*\)", "", text)
        text = re.sub("&amp;", " ", text)
        text = re.sub("&nbsp;", " ", text)
        text = re.sub("&lg;", " ", text)
        text = re.sub("&gt;", " ", text)
        # extra rules
        for rule in extraRules:
            text = re.sub(rule.lower(), "", text)
        # The following operations must be performed at the end.
        text = re.sub("[\n]+", "\n", text)
        text = re.sub('"', " ", text)  # repace  " character with space
        text = re.sub(",", " ", text)  # replace comma character with space
        text = re.sub(r"\.", " ", text)  # replace point character with space
        text = re.sub(";", " ", text)  # replace ; character with space
        text = re.sub(":", " ", text)  # replace ; character with space

        splitRE = "<"+splitTag+r">[\s\S]*?</"+splitTag+">"
        texts = re.findall(splitRE, text)
        if texts.count == 0:
            print("split fail")
            return
        for t in texts:
            outputFile = self.outputFilePath+str(self.nameIndex)
            self.nameIndex = self.nameIndex + 1
            with open(outputFile, "w", encoding="utf-8") as f_write:
                f_write.write(t)


def allfilepaths(inputDir, containHidden=False):
    inputFileNames = []
    for root, _, files in os.walk(inputDir):
        for afile in files:
            if '.' not in afile or containHidden == True:
                inputFileName = root+'/'+afile
                inputFileNames.append(inputFileName)
    return inputFileNames

def load_stopwords():
    pass

def generateQueryModel(workPath):
    # train word2vec
    texts = ""
    for f in allfilepaths(workPath):
        with open(f, "r", encoding="utf-8") as f_read:
            texts += f_read.read()
    texts = texts.lower()
    texts = re.sub(r"<.*?>", "", texts)
    #texts = re.sub(r"[^(a-zA-Z0-9)\n \S]", "", texts)
    texts = [text for text in texts.split('\n') if text.strip() != ""]
    ok_texts = [text.split() for text in texts]
    # # keep "wordA wordB" header integrited.
    # for text in texts:
    #     if len(text.split()) < 3:
    #         ok_texts.append(text)
    #     else:
    #         ok_texts.append(text.split())
    print(ok_texts)
    model = Word2Vec(ok_texts, size=100, window=5, min_count=1, workers=6)
    model.save("word2vec.model")


def query(queries, workPath):

    g = Graph(workPath, 3)
    return g.search(queries)


def show(res):
    for v in res:
        print("\nScore: ", int(v.p), "\nlevel: ", v.level, "\n text: (",
              v.text[:50].strip().replace("\n", " "), ")")


def preprocess(inputPath, workPath):
    wikiProcessor(inputPath, workPath).run()
    generateQueryModel(workPath)


def test():
    pass


debug = False
if __name__ == "__main__":
    if debug:
        wikiProcessor(args.input_path, args.work_path).run()
        generateQueryModel(args.work_path)
        res = query(["anarchism"], "/Users/emiles/Development/biye/temp/")
        show(res)
        exit(0)
    if args.preprocess:
        preprocess(args.input_path, args.work_path)
    elif args.query:
        res = query(args.query, args.work_path)
        show(res)

"""
config:
python3 xmlParser.py --input /Users/emiles/Development/biye/wikiextractor/text/   --work /Users/emiles/Development/biye/temp/ -p
python3 xmlParser.py -q  anarchism   --work /Users/emiles/Development/biye/temp
"""