import re
import os


# [remark] : vertex should not be changed by dot grammar
class vertex:
    def __init__(self, h, txt):
        self.h = h  # level position
        self.txt = txt  # innerHTML
        self.children = []  # child nodes
        self.tf = {}  # term frequencies    e.g.{$term:frequency}

    def getDescendants(self):
        if len(self.children) == 0:
            return self
        else:
            return [c.getDescendants() for c in self.children]

    # [method] return the frequency of the term
    # [params] term should only contains printable character
    def getTF(self, term):
        if term in self.tf:
            return self.tf[term]
        else:
            self.tf[term] = len(re.findall(term, self.txt))
            return self.tf[term]


# [parms] inputDir : output path of wikiStanderdize
#            level : max overlaping level
# [todo] adapt for any xml tag
class graph:
    def __init__(self, inputFilePath, level=4):
        self.inputFilePath = inputFilePath
        self.level = level  # max overlaping level
        self.endNum = 0  # num of the last layer
        self.roots = []  # document's roots
        self.terms = {}  # {term:idf}

        # init roots
        for f in allfilepaths(self.inputFilePath):
            with open(f, "r", encoding="utf-8") as f_read:
                docStr = f_read.read()
                self.roots.append(graph.getDocNodes(docStr, level))

        # init terms
        for t in self.getAllTerminologys(level):
            self.terms[t] = 0

        # init endNum
        for root in self.roots:
            for n in root.getDescendants():
                if n.level == self.level:
                    self.endNum += 1

    def setIDF(self):
        pass

    def setTF(self):
        pass

    def propagateTF(self):
        pass

    def propagateIDF(self):
        pass

    def getAllTerminologys(self, level):
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
    def getDocNodes(txt, maxDeep=4, h=1):
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
                    children.append(graph.getDocNodes(i[0], maxDeep, h+1))
        v = vertex(h - 1, re.sub(r'<.*>', "", txt))
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
        txt = re.sub("<li>.*</li>", "", txt)
        txt = re.sub(r"<ul>[\s\S]*?</ul>", "", txt)
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


def init():
    inputFilePath = "/Users/ethan/Development/wikiextractor/text2/"
    outputFilePath = "/Users/ethan/Development/temp/s/"

    wp = wikiProcessor(inputFilePath, outputFilePath)
    # wp.run()
    t = graph(outputFilePath, 3)


if __name__ == "__main__":
    init()
