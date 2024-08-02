import sys
import networkx as nx


class Workflow:
    def __init__(self, name, dot_file_path):
        self.name = name
        self.wf = nx.Graph(nx.nx_pydot.read_dot(dot_file_path))

    def _get_label(self, node):
        try:
            label = self.wf.nodes[node]['label'].lower()
        except KeyError:
            print(f'node {node} has no label', file=sys.stderr)
            exit(-1)
        return label

    def get_tasks(self):
        return [self._get_label(node) for node in self.wf.nodes]

    def get_dependencies(self):
        return {(self._get_label(e[0]), self._get_label(e[1])) for e in self.wf.edges}
