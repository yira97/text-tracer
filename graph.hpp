//
//  graph.hpp
//  nlp
//
//  Created by Ethan Miles on 2019/3/29.
//  Copyright © 2019 Ethan Miles. All rights reserved.
//

#ifndef graph_h
#define graph_h

#include <algorithm>
#include <array>
#include <iostream>
#include <memory>
#include <set>
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
        std::array<bool, maxStatusesType> statuses{false};
        
    public:
        Node() = default;
        Node(std::string name) : name(std::move(name)) {}
        ~Node() = default;
        
        void addStatusType(std::vector<NODE_STATUS> const &statuses) {
            for (NODE_STATUS const &s : statuses) {
                this->statuses[s] = true;
            }
        };
    };  // class Node
    
    class Edge {
    private:
        //
    public:
        Edge() = default;
        ~Edge() = default;
    };  // class Edge
    
    class Graph {
    private:
        std::string name;
        std::vector<std::shared_ptr<Node>> nodes;
        std::vector<std::shared_ptr<Edge>> edges;
        std::vector<std::vector<std::shared_ptr<Edge>>> adjacentList;
        
    public:
        Graph() = default;
        Graph(std::string name) : name(std::move(name)) {}
        ~Graph() = default;
        void printGraph() {
            for (int i = 0; i < nodes.size(); ++i) {
                std::cout << "Node-" << i << " : " << std::endl;
                for (int j = 0; j < nodes.size(); ++j) {
                    if (adjacentList[i][j]!=nullptr) {
                        std::cout << "         " << '(' << j << ')' << std::endl;
                    }
                    
                }
            }
        }
        bool connected(std::shared_ptr<Node> const &from,
                       std::shared_ptr<Node> const &to) {
            if (from == to) {
                return true;
            }
            
            std::vector<std::shared_ptr<Node>> children = outNodes(from);
            bool result = false;
            
            for (auto const &child : children) {
                if (connected(child, to)) {
                    result = true;
                    break;
                }
            }
            return result;
        }
        
        void addNode(std::shared_ptr<Node> const &node) {
            this->nodes.push_back(node);
            for (auto &line : this->adjacentList) {
                line.resize(nodes.size(), nullptr);  // new column
            }
            this->adjacentList.emplace_back(nodes.size(), nullptr);  // new row
        }
        
        void addEdge(std::shared_ptr<Node> const &from,
                     std::shared_ptr<Node> const &to) {
            // check DAG
            if (connected(to, from)) {
                std::cout << "found cycle path" << std::endl;
                return;
            }
            size_t indexFrom = indexOfNode(from);
            size_t indexTo = indexOfNode(to);
            
            if ((indexFrom >= this->nodes.size()) || (indexTo >= this->nodes.size())) {
                std::cout << "index over limit" << std::endl;
                return;
            }
            if (this->adjacentList[indexFrom][indexTo] != nullptr) {
                std::cout << "edge already exist" << std::endl;
                return;
            }
            std::shared_ptr<Edge> e = std::make_shared<Edge>();
            this->edges.push_back(e);
            this->adjacentList[indexFrom][indexTo] = e;
        }
        
        // if distance equal to number of nodes, proving that node doesn't exist.
        std::size_t indexOfNode(std::shared_ptr<Node> const &node) {
            auto it = std::find(this->nodes.cbegin(), this->nodes.cend(), node);
            return std::distance(this->nodes.cbegin(), it);
        }
        
        std::vector<std::shared_ptr<Node>> outNodes(
                                                    std::shared_ptr<Node> const &from) {
            auto const index = indexOfNode(from);
            
            std::vector<std::shared_ptr<Node>> res;
            for (std::size_t i = 0; i < this->nodes.size(); ++i) {
                if (this->adjacentList[index][i] != nullptr) {
                    res.push_back(nodes[i]);
                }
            }
            return res;
        };
        
        std::vector<std::shared_ptr<Edge>> outEdges(
                                                    std::shared_ptr<Node> const &from) {
            auto const index = indexOfNode(from);
            
            std::vector<std::shared_ptr<Edge>> res;
            for (std::size_t i = 0; i < this->nodes.size(); ++i) {
                if (this->adjacentList[index][i] != nullptr) {
                    res.push_back(adjacentList[index][i]);
                }
            }
            return res;
        }
        
        // return huge number in pair when fail to find edge.
        std::pair<std::size_t, std::size_t> edge_search(
                                                        std::shared_ptr<Edge> const &edge) const {
            for (std::size_t i = 0; i < this->nodes.size(); ++i) {
                for (std::size_t j = 0; j < this->nodes.size(); ++j) {
                    if (this->adjacentList.at(i).at(j) == edge) {
                        return std::make_pair(i, j);
                    }
                }
            }
            auto const tmp = std::numeric_limits<std::size_t>::max();
            return std::make_pair(tmp, tmp);
        }
        
        std::vector<std::shared_ptr<Node>> inNodes(
                                                   std::shared_ptr<Node> const &from) {
            auto const index = indexOfNode(from);
            
            std::vector<std::shared_ptr<Node>> res;
            for (std::size_t i = 0; i < this->nodes.size(); ++i) {
                if (this->adjacentList[i][index] != nullptr) {
                    res.push_back(nodes[i]);
                }
            }
            return res;
        };
        std::vector<std::shared_ptr<Edge>> inEdges(
                                                   std::shared_ptr<Node> const &from) {
            auto const index = indexOfNode(from);
            
            std::vector<std::shared_ptr<Edge>> res;
            for (std::size_t i = 0; i < this->nodes.size(); ++i) {
                if (this->adjacentList[i][index] != nullptr) {
                    res.push_back(adjacentList[i][index]);
                }
            }
            return res;
        };
    };
    
}  // namespace bys

#endif /* graph_h */
