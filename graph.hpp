#ifndef _0321_GRAPH_H
#define _0321_GRAPH_H

#include<vector>
#include<memory>
#include<string>



class Node
{
private:
    std::string nodeName;
public:
    Node() = delete;
    Node(std::string name);
    ~Node();
};

Node::Node(std::string name):nodeName(name)
{

}

Node::~Node()
{
}


class Edge
{
private:
    /* data */
public:
    Edge(/* args */);
    ~Edge();
};

Edge::Edge(/* args */)
{
}

Edge::~Edge()
{
}


class Graph
{
private:
    std::string graphName;
    std::vector<std::shared_ptr<Node>> nodes;
    std::vector<std::shared_ptr<Edge>> edges;

public:
    Graph() = delete;
    Graph(std::string name);

    ~Graph();
};

Graph::Graph(std::string name):graphName(name)
{
    
}


Graph::~Graph()
{
}

}



#endif