from os import path

NODES = ['a1', 'a2', 'c2', 'local', 'n1', 'n2']
NODE_FILE = path.join('data', 'machines.csv')
WORKFLOWS = ['atacseq', 'bacass', 'chipseq', 'eager', 'methylseq',
             'atacseq-workflow_30000', 'chipseq-workflow_20000', 'eager-workflow_1000', 'eager-workflow_8000',
             'methylseq-workflow_25000', 'atacseq-workflow_10000', 'atacseq-workflow_4000', 'chipseq-workflow_2000',
             'eager-workflow_15000', 'methylseq-workflow_30000', 'atacseq-workflow_1000', 'atacseq-workflow_8000',
             'chipseq-workflow_200', 'eager-workflow_18000', 'methylseq-workflow_10000', 'methylseq-workflow_4000',
             'atacseq-workflow_15000', 'chipseq-workflow_25000', 'eager-workflow_20000', 'methylseq-workflow_1000',
            'methylseq-workflow_8000', 'atacseq-workflow_18000', 'chipseq-workflow_30000', 'eager-workflow_2000',
             'methylseq-workflow_15000', 'atacseq-workflow_20000', 'chipseq-workflow_10000', 'chipseq-workflow_4000',
             'eager-workflow_200', 'methylseq-workflow_18000', 'atacseq-workflow_2000', 'chipseq-workflow_1000',
             'chipseq-workflow_8000', 'eager-workflow_25000', 'methylseq-workflow_20000',
             'atacseq-workflow_200', 'chipseq-workflow_15000', 'eager-workflow_30000', 'methylseq-workflow_2000',
             'atacseq-workflow_25000', 'chipseq-workflow_18000', 'eager-workflow_10000', 'eager-workflow_4000',
             'methylseq-workflow_200']
WF_DOT_FILE_MAP = {wf: path.join('data', 'workflows', f'{wf}.dot')
                   for wf in WORKFLOWS}
TRACE_FILE = path.join('data', 'traces.csv')
TRACE_HEADER = {
    'workflow': 'string',
    'inputsize': 'int64',
    'task': 'string',
    'machine': 'string',
    'time': 'int64',
    'memory': 'int64',
    'wchar': 'int64',
    'taskinputsize': 'int64'
}
THRESHOLD = 0.1
URL = 'http://localhost:'
