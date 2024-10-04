import sys
import networkx as nx
import pandas as pd
import numpy as np
import re
from .constants import (
    TRACE_FILE,
    TRACE_HEADER,
    WORKFLOWS,
    WF_DOT_FILE_MAP,
    NODE_FILE,
)
from .workflow import Task

def strip_numbers(s):
    sub = s.strip('\'" ')
    sub = re.sub(r'_\d+$', '', sub)
    return sub

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
    workflow = workflow.strip()
    workflow_file = WF_DOT_FILE_MAP[workflow]
    nx_graph = nx.DiGraph(nx.nx_pydot.read_dot(workflow_file))
    for node in nx_graph.nodes:
        node_name = _nx_get_node_name(nx_graph, node)
        deps = {_nx_get_node_name(nx_graph, edge[0])
                for edge in nx_graph.in_edges(node)}
        graph[node_name] = deps
    # get traces
    traces = pd.read_csv(TRACE_FILE, dtype=TRACE_HEADER)
    traces.set_index(
        ['workflow', 'inputsize', 'task', 'machine'], inplace=True)
    workflow_short_name = workflow.split('-')
    traces = traces.loc[(workflow_short_name[0], input_size)]
    # get machine info
    machines = pd.read_csv(NODE_FILE, index_col='machine', usecols=[
                           'machine', 'cpu_events'])
    machines.rename(columns={'cpu_events': 'speed'}, inplace=True)
    for task_name in graph.keys():
        task_name_lookup = strip_numbers(task_name)
        for machine in machines.index:
            if (task_name_lookup, machine) not in traces.index:
                traces.loc[(task_name_lookup, machine), :] = [1, 5e7, 1000 ,1000]
    # load tasks
    tasks = {}
    for task_name, deps in graph.items():
        task_name_lookup = strip_numbers(task_name)
        work = int(np.mean(traces.loc[task_name_lookup]['time'] * machines['speed']))
        memory = int(np.mean(traces.loc[task_name_lookup]['memory']))
        wchar = int(np.mean(traces.loc[task_name_lookup]['wchar']))
        taskinputsize = int(np.mean(traces.loc[task_name_lookup]['taskinputsize']))
        tasks[task_name] = Task(task_name, deps, work, memory, wchar, taskinputsize)
        if task_name_lookup == "check_design":
            tasks[task_name].work_predicted= 2*tasks[task_name].work
    return tasks
