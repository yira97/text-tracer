import re
import os
import sys
import argparse
import math

parser = argparse.ArgumentParser(
    description="document indexing script using bayesian network. for more information see https://github.com/ethanmiles/Bayesian-Network-for-NLP")
parser.add_argument('--input', type=str,
                    help='directory hold result of wikiextractor')
parser.add_argument('--output', type=str, help='work directory')

group = parser.add_mutually_exclusive_group()
group.add_argument('-p', '--preprocess',
                   action='store_true', help='preprocess')
group.add_argument('-q', '--query', nargs='+', help='query')

args = parser.parse_args()


# [remark] : Vertex should not be changed by dot grammar
class Vertex:

    def __init__(self, h, txt):
        self.h = h  # level position
        self.txt = txt  # innerHTML
        self.children = []  # child nodes
        self.tf = {}  # term frequencies    e.g.{$term:frequency}
        self.p = 0

    def getDescendants(self):
        l = []
        Vertex.GetDescendants(self, l)
        return l

    @staticmethod  # For more general purposes
    def AllVertexFromVertexs(vs):
        l = []
        for v in vs:
            Vertex.GetDescendants(v, l)
        return l

    @staticmethod
    def GetDescendants(v, l):
        for c in v.children:
            Vertex.GetDescendants(c, l)
        l.append(v)

    # [method] return the frequency of the term
    # [params] term should only contains printable character
    def getTF(self, term):
        if term in self.tf:
            return self.tf[term]
        else:
            self.setTF(term)
            return self.tf[term]

    def setTF(self, term):
        self.tf[term] = len(re.findall(term, self.txt))

    # def getDady(self, crowd):
    #     for men in crowd:
    #         if self in men.children:
    #             return men
        # print("poor boy.")

    # def countBro(self, crowd):
    #     return len(self.getDady(crowd).children)


# [parms] inputDir : output path of wikiStanderdize
#            level : max overlaping level
# [todo] adapt for any xml tag


class Graph:
    def __init__(self, inputFilePath, level=4):
        self.inputFilePath = inputFilePath
        self.level = level  # max overlaping level
        self.layerNum = {}  # num of the every layer
        for i in range(0, level+1):
            self.layerNum[i] = 0
        self.roots = []  # document's roots
        self.terms = {}  # {term: {level:count} }

        # init roots
        for f in allfilepaths(self.inputFilePath):
            with open(f, "r", encoding="utf-8") as f_read:
                docStr = f_read.read()
                self.roots.append(Graph.GetDocNodes(docStr, level))

        # init terms (must before init layer number)
        for t in self.getAllTerminologys():
            self.terms[t] = self.layerNum.copy()

        # init layer number
        for v in Vertex.AllVertexFromVertexs(self.roots):
            self.layerNum[v.h] += 1

        # init idf
        self.setIDF()
        self.setDF()

    def setIDF(self):
        allVertexs = Vertex.AllVertexFromVertexs(self.roots)
        for t in self.terms:
            for v in allVertexs:
                if t in v.txt:
                    self.terms[t][v.h] += 1
        for t in self.terms:
            for h in self.terms[t]:
                if self.terms[t][h] > 0:
                    self.terms[t][h] = self.layerNum[h] / self.terms[t][h]
                else:
                    self.terms[t][h] = 0

    # return max level at default

    def getIDF(self, termName, level=0):
        if level == 0:
            level = self.level
        return self.terms[termName][level]

    def setDF(self):
        for v in Vertex.AllVertexFromVertexs(self.roots):
            if v.h == self.level:
                for t in self.getAllTerminologys():
                    v.getTF(t)
            else:
                pass  # note which doesn't direct connect with terminoloty do not have df

    # def setWeight(self):
        # for n in Vertex.AllVertexFromVertexs(self.roots):
        #     count = 0
        #     if n.h == self.level:
        #         for t in self.getAllTerminologys():
        #             ttf = n.getTF(t)
        #             if ttf > 0:
        #                 count += ttf*self.getIDF(t)
        #         n.p = count
        #     else:
        #
        #             if n in parent.children:
        #                 count += 1
        #         if count > 0:
        #             n.p = 1/count
        #         else:
        #             n.p = 0

    def getWeight(self, n1, n2):
        if n2.h == self.level:  # n1 is terminology
            idf = self.terms[n1][self.level]
            if idf > 0:
                return n2.getTF(n1) * math.log10(idf)
            else:
                return 0
        else:  # n1 is parent node
            for n in Vertex.AllVertexFromVertexs(self.roots):
                if n1 in n.children:
                    return 1 / len(n.children)

    def search(self, queries):
        ns = Vertex.AllVertexFromVertexs(self.roots)
        # first process the end level
        for n in ns:
            if n.h == self.level:
                n.p = 0
                for t in self.terms:
                    if t in queries:
                        n.p += self.getWeight(t, n)
                    else:
                        n.p += self.getWeight(t, n) / len(t)
        # process from second end level to root level
        for i in range(self.level-1, 0, -1):
            for n in ns:
                if n.h == i:
                    num = len(n.children)
                    if num > 0:
                        for c in n.children:
                            n.p += (c.p * (1/num))
                        #print("来自level", i, '的结点继承了', n.p, '分！')
                    else:
                        n.p = 0

        for n in ns:
            print("来自 level", n.h, " 的结点，得到了 ",
                  n.p, "的分数。")

    def getAllTerminologys(self, level="undefine"):
        if level == "undefine":
            level = self.level
        terms = []
        stri = ""
        for i in range(1, level+1):
            stri += str(i)
        for f in allfilepaths(self.inputFilePath):
            with open(f, "r", encoding="utf-8") as f_read:
                txt = f_read.read()
                for t in re.findall(r"<h["+stri+r"]>(.*?)</h\d>", txt):
                    terms.append(t)
        return set(terms)

    # [params] do not pass h paramerter.
    @staticmethod
    def GetDocNodes(txt, maxDeep=4, h=1):
        if len(txt) == 0:
            return
        stri = r"<h"+str(h)+r">.*?</h"+str(h) + \
            r">([\s\S]*?)(?=<h" + str(h)+r">(.*?)</h"+str(h)+r")"
        inners = re.findall(stri, txt)

        if len(inners) > 0:
            strLast = r"<h"+str(h)+r">" + \
                inners[-1][-1]+r"</h"+str(h)+r">([\s\S]*)"
        else:
            strLast = r"<h"+str(h)+r">.*?</h"+str(h)+r">([\s\S]*)"
        last = re.findall(strLast, txt)
        if len(last) > 0:
            inners.append((last[0], ""))
        children = []
        if len(inners) != 0:
            for i in inners:
                if (h <= maxDeep):
                    children.append(Graph.GetDocNodes(i[0], maxDeep, h+1))
        v = Vertex(h - 1, re.sub(r'<.*>', "", txt))
        v.children = children
        return v


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

    def standerdize(self, extraRules, splitTag="doc"):

        with open(self.inputFilePath, "r", encoding="utf-8") as f_read:
            txt = f_read.read()

        txt = re.sub("<doc.*>", "<doc>", txt)
        txt = re.sub(r"<li>.*</li>", "", txt)
        txt = re.sub(r"<ul>[\s\S]*?</ul>", "", txt)
        txt = re.sub(r"<ol>[\s\S]*?</ol>", "", txt)
        txt = re.sub("</ul>", "", txt)
        txt = re.sub("&lt;/a&gt;", "", txt)
        txt = re.sub("&lt;a href=.*?&gt;", "", txt)
        txt = re.sub(r"\[.*\]", " ", txt)
        txt = re.sub(r"\(.*\)", "", txt)
        txt = re.sub("&amp;", " ", txt)
        txt = re.sub("&nbsp;", " ", txt)
        txt = re.sub("&lg;", " ", txt)
        txt = re.sub("&gt;", " ", txt)
        # extra rules
        for rule in extraRules:
            txt = re.sub(rule, "", txt)
        # The following operations must be performed at the end.
        txt = re.sub("[\n]+", "\n", txt)
        txt = re.sub('"', " ", txt)  # repace  " character with space
        txt = re.sub(",", " ", txt)  # replace comma character with space
        txt = re.sub(r"\.", " ", txt)  # replace point character with space
        txt = re.sub(";", " ", txt)  # replace ; character with space
        txt = re.sub(":", " ", txt)  # replace ; character with space

        splitRE = "<"+splitTag+r">[\s\S]*?</"+splitTag+">"
        txts = re.findall(splitRE, txt)
        if txts.count == 0:
            print("split fail")
            return
        for t in txts:
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


def query(wp, queries):
    g = Graph(outputFilePath, 3)
    g.search(queries)


def preprocess(wp):
    wp.run()


def test():
    pass


if __name__ == "__main__":
    inputFilePath = "/Users/ethan/Documents/Development/wikiextractor/text2/"
    outputFilePath = "/Users/ethan/Documents/Development/temp/s/"

    wp = wikiProcessor(inputFilePath, outputFilePath)

    debug = False
    if debug:
        query(wp, ["Feedback"])
        exit(0)

    if args.preprocess:
        preprocess(wp)
    elif args.query:
        print("query slice : ", args.query)
        query(wp, args.query)
    print("")
