from os import path
NODES = ['asok01', 'asok02', 'c2', 'local', 'n1', 'n2']
NODE_FILE = path.join('data', 'nodes.csv')
WORKFLOWS = ['atacseq', 'bacass', 'chipseq', 'eager', 'methylseq']
WF_DOT_FILE_MAP = {wf: path.join('data', 'workflows', f'{wf}.dot')
                   for wf in WORKFLOWS}
TRACE_FILE = path.join('data', 'traces.csv')
TRACE_HEADER = {
    'workflow':     'string',
    'inputsize':    'int64',
    'task':         'string',
    'machine':      'string',
    'time':         'int64',
}
URL = 'http://localhost:9900'
