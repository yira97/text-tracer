//
//  main.cpp
//  nlp
//
//  Created by Ethan Miles on 2019/3/29.
//  Copyright © 2019 Ethan Miles. All rights reserved.
//

#include <iostream>
#include "graph.hpp"
#include "xml_parser.hpp"
int main(int argc, char const *argv[]) {
    //structure_test();
    
    //xmlParser("/Users/ethan/Downloads/enwiki-latest-pages-articles.xml","/Users/ethan/temp/")
    xmlParser xp ("/Users/ethan/Documents/Proj/xcode/Bayesian-Network-for-NLP/bayesian_network_for_nlp/test_split.html","/Users/ethan/temp/");
    xp.splitToFiles("fuck", 1000);
    return 0;
}
