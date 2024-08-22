import sys
import networkx as nx
from graphviz import Digraph


def _nx_get_node_name(nx_graph, node):
    try:
        label = nx_graph.nodes[node]['label'].lower()
    except KeyError:
        print(f'node {node} has no label', file=sys.stderr)
        exit(-1)
    return label


class Workflow:
    def __init__(self, name, dot_file_path):
        self.name = name
        # maps from a tasks name to the names of its parents
        self.graph = {}
        nx_graph = nx.DiGraph(nx.nx_pydot.read_dot(dot_file_path))
        for node in nx_graph.nodes:
            node_name = _nx_get_node_name(nx_graph, node)
            deps = {_nx_get_node_name(nx_graph, edge[0])
                    for edge in nx_graph.in_edges(node)}
            self.graph[node_name] = deps
        # self.show_graph()

    def show_graph(self):
        dot = Digraph()
        for name, deps in self.graph.items():
            dot.node(name, name)
            for dep in deps:
                dot.edge(dep, name)
        dot.view()

    def get_deps(self, task):
        return self.graph[task]

    def get_tasks(self):
        return self.graph.keys()
