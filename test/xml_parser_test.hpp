
//
//  xml_parser_test.hpp
//  bayesian_network_for_nlp
//
//  Created by Ethan Miles on 2019/3/30.
//  Copyright © 2019 Ethan Miles. All rights reserved.
//

#ifndef xml_parser_test_h
#define xml_parser_test_h
#include "../xml_parser.hpp"
// xmlParser("/Users/ethan/Downloads/enwiki-latest-pages-articles.xml","/Users/ethan/temp/")
xmlParser xp(
    "/Users/ethan/Documents/Proj/xcode/Bayesian-Network-for-NLP/"
    "bayesian_network_for_nlp/test_split.html",
    "/Users/ethan/temp/");

xp.splitToFiles("fuck", 1000);

#endif /* graph_test_h */