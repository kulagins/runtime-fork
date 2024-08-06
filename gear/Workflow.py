import sys
import networkx as nx


class Workflow:
    def __init__(self, name, dot_file_path):
        self.name = name
        self.nx_graph = nx.DiGraph(nx.nx_pydot.read_dot(dot_file_path))
        self.graph = {}
        for node in self.nx_graph.nodes:
            node_name = self._nx_get_node_name(node)
            deps = {self._nx_get_node_name(edge[0])
                    for edge in self.nx_graph.in_edges(node)}
            self.graph[node_name] = deps
        self.done_tasks = set()

    def _nx_get_node_name(self, node):
        try:
            label = self.nx_graph.nodes[node]['label'].lower()
        except KeyError:
            print(f'node {node} has no label', file=sys.stderr)
            exit(-1)
        return label

    def get_tasks(self):
        return self.graph.keys()

    def task_mark_done(self, task):
        self.done_tasks.add(task)

    def task_is_ready(self, task):
        for dep in self.graph[task]:
            if dep not in self.done_tasks:
                return False
        return True

    def workflow_is_finished(self):
        return set(self.graph.keys()) == self.done_tasks
