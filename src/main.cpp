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
  xmlParser xpsr{"/Users/ethan/Downloads/enwiki-latest-pages-articles.xml",
                 "test/temp"};
  xpsr.splitToFiles("page", 1000000);
  return 0;
}
