import re
import os

nameIndex = 1


class vertex:
    def __init__(self, h, txt):
        self.h = h
        self.txt = txt
        self.children = []


class graph:
    def __init__(self, inputDir, deep=4):
        self.roots = []
        self.terms = []

        for f in allfilepaths(inputDir):
            with open(f, "r", encoding="utf-8") as f_read:
                docStr = f_read.read()
                self.roots.append(getDocNodes(docStr, deep))

        self.terms = getAllTerminologys(inputDir, deep)


def getDocNodes(txt, maxDeep=4, h=1):  # do not pass h paramerter.
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
                children.append(getDocNodes(i[0], maxDeep, h+1))
    v = vertex(h - 1, txt)
    v.children = children
    return v


def allfilepaths(inputDir, containHidden=False):
    inputFileNames = []
    for root, _, files in os.walk(inputDir):
        for afile in files:
            if '.' not in afile or containHidden == True:
                inputFileName = root+'/'+afile
                inputFileNames.append(inputFileName)
    return inputFileNames


def getAllTerminologys(inputDir, deep):
    terms = []
    stri = ""
    for i in range(1, deep+1):
        stri += str(i)
    for f in allfilepaths(inputDir):
        with open(f, "r", encoding="utf-8") as f_read:
            txt = f_read.read()
            for t in re.findall(r"<h["+stri+r"]>(.*?)</h\d>", txt):
                terms.append(t)
    return set(terms)


def wikiStanderdize(inputDir, outputDir):

    rule = [r"<doc>.*?<h1>.*?</h1>\n.*?may refer to[\s\S]*?</doc>", r"<h2>See also</h2>", r"<h2>References</h2>",
            r"<h3>Specific</h3>", r"<h3>General</h3>", r"<h2>External links</h2>"]
    for f in allfilepaths(inputDir):
        print("start process : ", f)
        standerdize(f, outputDir, rule)


def standerdize(inputFilePath, outputDir, extraRules, splitTag="doc"):
    global nameIndex

    with open(inputFilePath, "r", encoding="utf-8") as f_read:
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
        outputFile = outputDir+str(nameIndex)
        nameIndex = nameIndex + 1
        with open(outputFile, "w", encoding="utf-8") as f_write:
            f_write.write(t)


def init():
    #inputFilePath = "/Users/ethan/Development/wikiextractor/text2/"
    outputFilePath = "/Users/ethan/Development/temp/s/"

    # wikiStanderdize(inputFilePath, outputFilePath)
    t = graph(outputFilePath, 3)
    print(t)


if __name__ == "__main__":
    init()
