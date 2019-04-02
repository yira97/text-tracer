import re
import os
# extraRule need dict of string type re

nameIndex = 1


def wikiStanderdize(inputDir, outputDir):
    rule = ["<doc>.*?<h1>.*?</h1>\n.*?may refer to[\s\S]*?</doc>", "<h2>See also</h2>", "<h2>References</h2>",
            "<h3>Specific</h3>", "<h3>General</h3>", "<h2>External links</h2>"]
    for root, _, files in os.walk(inputDir):
        for afile in files:
            if '.' not in afile:
                inputFileName = root+'/'+afile
                print("start process : ", inputFileName)
                standerdize(inputFileName, outputDir, rule)


def standerdize(inputFilePath, outputDir, extraRules, splitTag="doc"):
    global nameIndex

    with open(inputFilePath, "r", encoding="utf-8") as f_read:
        txt = f_read.read()

    txt = re.sub("<doc.*>", "<doc>", txt)
    txt = re.sub("<li>.*</li>", "", txt)
    txt = re.sub("<ul>[\s\S]*?</ul>", "", txt)
    txt = re.sub("</ul>", "", txt)
    txt = re.sub("&lt;/a&gt;", "", txt)
    txt = re.sub("&lt;a href=.*?&gt;", "", txt)
    txt = re.sub("\[.*\]", " ", txt)
    txt = re.sub("\(.*\)", "", txt)
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
    txt = re.sub("\.", " ", txt)  # replace point character with space
    txt = re.sub(";", " ", txt)  # replace ; character with space
    txt = re.sub(":", " ", txt)  # replace ; character with space

    splitRE = "<"+splitTag+">[\s\S]*?</"+splitTag+">"
    txts = re.findall(splitRE, txt)
    if txts.count == 0:
        print("split fail")
        return
    for t in txts:
        outputFile = outputDir+str(nameIndex)
        nameIndex = nameIndex + 1
        with open(outputFile, "w", encoding="utf-8") as f_write:
            f_write.write(t)


if __name__ == "__main__":
    inputFilePath = "/Users/ethan/Development/wikiextractor/text2/"
    outputFilePath = "/Users/ethan/Development/temp/s/"
    wikiStanderdize(inputFilePath, outputFilePath)
