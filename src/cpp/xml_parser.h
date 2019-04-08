//
//  xmlParser.h
//  bayesian-network-for-nlp
//
//  Created by Ethan Miles on 2019/3/31.
//  Copyright © 2019 Ethan Miles. All rights reserved.
//

#ifndef xmlParser_h
#define xmlParser_h

#include <fstream>
#include <iostream>
#include <string>
#include <algorithm>
#include <streambuf>
#include <regex>
#include "log.h"

class node {
    std::string tag;
    std::string::const_iterator beg;
    std::string::const_iterator end;
    std::vector<node> children;

public:
    node() = delete;
    node(std::string tag):tag(std::move(tag)){};
    node(std::string tag,std::string::const_iterator beg,std::string::const_iterator end):tag(std::move(tag)),beg(beg),end(end) {};
    ~node() = default;
};

class xmlParser {
private:
    std::string defaultOutputPath;
public:
    xmlParser() = delete;
    xmlParser(std::string defaultOutput):defaultOutputPath(std::move(defaultOutput)) {};
    ~xmlParser() {
    };
    
        std::shared_ptr<node> generateDOM (std::string from, std::string rootTag) {
            std::ifstream originXML{from};
            if(!originXML.is_open()){
                log("!originXML.is_open()","fail to read");
                return nullptr;
            }
            std::string str{(std::istreambuf_iterator<char>(originXML)), std::istreambuf_iterator<char>()};
    
            node root {"_root_"};
    
            const std::string tagBegin = std::string("<") + rootTag + ">";
            const std::string tagEnd = std::string("</") + rootTag + ">";
    
            return std::make_shared<node>(root);
        }
    
    void enwikiProcess(std::string from, std::string to) {
        struct {
            std::string splitTag = "page";
            std::int64_t splitLines = 1000000;// 1,000,000
        } config;
        
        splitToFiles(from, config.splitTag, config.splitLines, to);
        
    }
    void wordFilter(string){
        
    }
    // check the intergity of the xml document.
    bool xmlIntegrity (std::istream& i){
        return false;
    }
    // [describe] split xml using default output path
    // [parameter] tag : "html" ( "<html>" is invalid),
    //             just split outside tag, doesn't process nested tag with same name.
    // [bug] may generate an extra blank file
    void splitToFiles(std::string from, std::string tag, int64_t maxProcessLines) {
        splitToFiles(from, tag, maxProcessLines, defaultOutputPath);
    }
    
    // [describe] split xml using assign path
    // [parameter] tag : "xxx" ( "<xxx>" is invalid)
    //             just split outside tag, doesn't process nested tag with same name.
    // [bug] may generate an extra blank file
    void splitToFiles(std::string from, std::string tag, int64_t maxProcessLines,
                      std::string outputDir) {
        std::ifstream originXML;
        originXML.open(from);
        if(!originXML.is_open()){
            log("!originXML.is_open()","fail to read");
            return ;
        }
        std::string tagBegin = std::string("<") + tag + ">";
        std::string tagEnd = std::string("</") + tag + ">";
        if(tag.compare("html") == 0){
            tagBegin = std::string("<") + tag + " xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\" dir=\"ltr\">";
        }
        int64_t currentLines = 0;
        std::string line;
        bool reading = false;
        bool empty = true;
        int dirIndex = 1;
        std::string validOutput;
        std::ofstream ostream{outputDir + std::to_string(dirIndex)};
        size_t endPos = 0;
        size_t beginPos = 0;
        
        for (; currentLines <= maxProcessLines;) {
            if (empty == true) {
                std::getline(originXML, line);
                ++currentLines;
            } else {
                line = line.substr(endPos + tagEnd.size(), -1);
                ++dirIndex;
                ostream.close();
                log("finished write file "+std::to_string(dirIndex),"");
                ostream.open(outputDir + std::to_string(dirIndex));
            }
            if (reading == true) {
                endPos = line.find(tagEnd, 0);
                if (endPos != -1) {
                    validOutput = line.substr(0, endPos);  // "+++++</T>?????"
                    reading = false;
                    empty = false;
                } else {
                    validOutput = line;  // "+++++++++++"
                    empty = true;
                    reading = true;
                }
            } else {  // (reading == false)
                beginPos = line.find(tagBegin, 0);
                if (beginPos != -1) {
                    endPos = line.find(tagEnd, 0);
                    if (endPos != -1) {
                        validOutput =
                        line.substr(beginPos + tagBegin.size(),
                                    endPos - beginPos -
                                    tagBegin.size());  //"-----<T>+++++++</T>?????"
                        reading = false;
                        empty = false;
                    } else {
                        validOutput =
                        line.substr(beginPos + tagBegin.size(), -1);  //"---<T>+++++++"
                        empty = true;
                        reading = true;
                    }
                } else {
                    validOutput = "";  //"---------"
                    empty = true;
                }
            }
            ostream << validOutput;
            
            if (originXML.eof()) {
                break;
            }
        }  // end for
        
        // postprocess
        if (ostream.is_open()) {
            ostream.close();
        }
        if(originXML.is_open()){
            originXML.close();
        }
    };
};

#endif /* xmlParser_h */
