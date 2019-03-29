//
//  main.cpp
//  nlp
//
//  Created by Ethan Miles on 2019/3/29.
//  Copyright © 2019 Ethan Miles. All rights reserved.
//

#include <iostream>
#include "graph.hpp"
using namespace bys;
int main(int argc, char const *argv[]) {
  Graph g("nlp");
  auto a = std::make_shared<Node>();
  auto b = std::make_shared<Node>();
  auto c = std::make_shared<Node>();
  auto d = std::make_shared<Node>();
  auto e = std::make_shared<Node>();
  g.addNode(a);
  g.addNode(b);
  g.addNode(c);
  g.addNode(d);
  g.addNode(e);

  g.addEdge(a, b);
  g.addEdge(b, c);
  g.addEdge(c, d);
  g.addEdge(c, e);
  g.addEdge(d, e);
  // g.addEdge(e,a);
  g.addEdge(e, e);
  g.printGraph();

  return 0;
}
