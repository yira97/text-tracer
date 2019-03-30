//
//  graph_test.hpp
//  bayesian_network_for_nlp
//
//  Created by Ethan Miles on 2019/3/30.
//  Copyright © 2019 Ethan Miles. All rights reserved.
//

#ifndef graph_test_h
#define graph_test_h

#include "../graph.hpp"

void structure_test() {
  using namespace bys;
  bys::Graph g("nlp");
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
  // g.addEdge(e, e);
  g.printGraph();
}

#endif /* graph_test_h */
