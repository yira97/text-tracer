#ifndef _0321_GRAPH_H
#define _0321_GRAPH_H

#include <algorithm>
#include <array>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

namespace bys {

enum NODE_STATUS {
  STATUS_FALSE,
  STATUS_TRUE,

  STATUS_A,
  STATUS_B,
  STATUS_C,
  STATUS_D,
  STATUS_E,

  STATUS_X,
  STATUS_Y,
  STATUS_Z,

  _STATUS_EOF  // do not use
};

constexpr size_t maxStatusesType = _STATUS_EOF;

class Node {
 private:
  std::string name;
  std::array<bool, maxStatusesType> statuses;

 public:
  Node() = delete;
  Node(std::string name);
  ~Node() = default;

  void addStatusType(std::vector<NODE_STATUS> statuses);
};

Node::Node(std::string name) : name(name) {}

Node::~Node() {}

void Node::addStatusType(std::vector<NODE_STATUS> statuses) {
  for (NODE_STATUS const &s : statuses) {
    this->statuses[s] = true;
  }
}

class Edge {
 private:
  /* data */
 public:
  Edge() = default;
  ~Edge() = default;
};

Edge::Edge(/* args */) {}

Edge::~Edge() {}

class Graph {
 private:
  std::string name;
  std::vector<std::shared_ptr<Node>> nodes;
  std::vector<std::shared_ptr<Edge>> edges;
  std::vector<std::vector<std::shared_ptr<Edge>>> adjacentList;

 public:
  Graph() = default;
  ~Graph() = default;
  Graph(std::string name);
  void addNode(std::shared_ptr<Node> const &node);
  void addEdge(std::shared_ptr<Node> const &from,
               std::shared_ptr<Node> const &to);
  size_t indexOfNode(std::shared_ptr<Node> const &node) {
    auto it = std::find(this->nodes.cbegin(), this->nodes.cend(), node);
    return std::distance(this->nodes.cbegin(), it);
  }
};

void Graph::addNode(std::shared_ptr<Node> const &node) {
  this->nodes.push_back(node);
  this->adjacentList.emplace_back(this->nodes.size(), nullptr);  // new row
  for (auto &line : this->adjacentList) {                        // new column
    line.emplace_back(1, nullptr);
  }
}
void Graph::addEdge(std::shared_ptr<Node> const &from,
                    std::shared_ptr<Node> const &to) {
  // todo:check validate of Edge
  size_t indexFrom = indexOfNode(from);
  size_t indexTo = indexOfNode(to);
  if ((indexFrom >= this->nodes.size()) || (indexTo >= this->nodes.size())) {
    std::cout << "index over limit";
    return;
  }
  if (this->adjacentList[indexFrom][indexTo] != nullptr) {
    std::cout << "edge already exist";
    return;
  }
  std::shared_ptr<Edge> e = std::make_shared<Edge>();
  this->edges.push_back(e);
  this->adjacentList[indexFrom][indexTo] = e;
}

Graph::Graph(std::string name) : name(name) {}

Graph::~Graph() {}

}  // namespace bys
#endif