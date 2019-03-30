//
//  xml_parser.hpp
//  bayesian_network_for_nlp
//
//  Created by Ethan Miles on 2019/3/29.
//  Copyright © 2019 Ethan Miles. All rights reserved.
//

#ifndef xml_parser_h
#define xml_parser_h

#include <iostream>
#include <string>
#include <set>
#include <fstream>

class xmlParser {
private:
    std::string inputPath;
    std::string outputPath;
    std::set<std::string> filterTable;
    
    std::ifstream originXML;
public:
    xmlParser() = delete;
    xmlParser(std::string input, std::string defaultOutput) : inputPath(std::move(input)), outputPath(std::move(defaultOutput)){
        originXML.open(inputPath);
        if (!originXML.is_open()) {
            std::cout << "failed to open " << inputPath << '\n';
        }
    };
    ~xmlParser() = default;
    
    // [describe] split xml using default output path
    // [parameter] tag : "xxx" ( "<xxx>" is invalid)
    // [bug] may generate an extra blank file
    void splitToFiles(std::string tag, int64_t maxProcessLines){
        splitToFiles(tag, maxProcessLines, outputPath);
    }
    
    // [describe] split xml using assign path
    // [parameter] tag : "xxx" ( "<xxx>" is invalid)
    // [bug] may generate an extra blank file
    void splitToFiles(std::string tag, int64_t maxProcessLines, std::string outputDir){
        std::string tagBegin = "<"+tag+">";
        std::string tagEnd = "</"+tag+">";
        int64_t currentLines = 0;
        std::string line;
        bool reading = false;
        bool empty = true;
        int dirIndex = 1;
        std::string validOutput;
        std::ofstream ostream {outputDir + std::to_string(dirIndex)};
        size_t endPos= 0 ;
        size_t beginPos = 0;
        
        for(; currentLines <= maxProcessLines;){
            if ( empty == true ){
                std::getline(originXML,line);
                ++currentLines;
            } else {
                line = line.substr(endPos+tagEnd.size(),-1);
                ++dirIndex;
                ostream.close();
                ostream.open(outputDir + std::to_string(dirIndex));
            }
            
            if (reading == true ){
                endPos = line.find(tagEnd,0);
                if (endPos != -1){
                    validOutput = line.substr(0,endPos);// "+++++</T>?????"
                    reading = false;
                    empty = false;
                }else{
                    validOutput = line;// "+++++++++++"
                    empty = true;
                    reading = true;
                }
            }else { // (reading == false)
                beginPos = line.find(tagBegin,0);
                if (beginPos != -1){
                    endPos = line.find(tagEnd,0);
                    if(endPos != -1) {
                        validOutput = line.substr(beginPos + tagBegin.size(),endPos - beginPos - tagBegin.size()); //"-----<T>+++++++</T>?????"
                        reading = false;
                        empty = false;
                    } else {
                        validOutput = line.substr(beginPos + tagBegin.size(),-1); //"---<T>+++++++"
                        empty = true;
                        reading = true;
                    }
                }else{
                    validOutput = ""; //"---------"
                    empty = true;
                }
            }
            ostream<<validOutput;
            
            if (originXML.eof()){
                break;
            }
        } //end for
        
        if (ostream.is_open()){
            ostream.close();
        }
    };
};

#endif /* xml_parser_h */
