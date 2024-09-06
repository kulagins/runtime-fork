import sys
import networkx as nx
import pandas as pd
import numpy as np
from .constants import (
    TRACE_FILE,
    TRACE_HEADER,
    WORKFLOWS,
    WF_DOT_FILE_MAP,
    NODE_FILE,
)
from .workflow import Task


def _nx_get_node_name(nx_graph, node):
    try:
        label = nx_graph.nodes[node]['label'].lower()
    except KeyError:
        print(f'node {node} has no label', file=sys.stderr)
        exit(-1)
    return label


def get_workflow_input_sizes():
    df = pd.read_csv(TRACE_FILE, dtype=TRACE_HEADER)
    input_sizes = {}
    for wf in WORKFLOWS:
        input_sizes[wf] = list(
            df[df['workflow'] == wf]['inputsize'].unique())
    return input_sizes


def get_workflow(workflow, input_size):
    # get workflow structure
    graph = {}
    nx_graph = nx.DiGraph(nx.nx_pydot.read_dot(WF_DOT_FILE_MAP[workflow]))
    for node in nx_graph.nodes:
        node_name = _nx_get_node_name(nx_graph, node)
        deps = {_nx_get_node_name(nx_graph, edge[0])
                for edge in nx_graph.in_edges(node)}
        graph[node_name] = deps
    # get traces
    traces = pd.read_csv(TRACE_FILE, dtype=TRACE_HEADER)
    traces.set_index(
        ['workflow', 'inputsize', 'task', 'machine'], inplace=True)
    traces = traces.loc[(workflow, input_size)]
    # get machine info
    machines = pd.read_csv(NODE_FILE, index_col='machine', usecols=[
                           'machine', 'cpu_events'])
    machines.rename(columns={'cpu_events': 'speed'}, inplace=True)
    for task_name in graph.keys():
        for machine in machines.index:
            if (task_name, machine) not in traces.index:
                traces.loc[(task_name, machine), :] = [1, 5e7]
    # load tasks
    tasks = {}
    for task_name, deps in graph.items():
        work = int(np.mean(traces.loc[task_name]['time'] * machines['speed']))
        memory = int(np.mean(traces.loc[task_name]['memory']))
        tasks[task_name] = Task(task_name, deps, work, memory)
    return tasks
