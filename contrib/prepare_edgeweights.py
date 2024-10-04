from io import StringIO
from os import path
import pandas as pd
import numpy as np
'''
This script prepares our lotaru trace files for use in this project. It expects
the folder 'tasks_lotaru' in the current working directory and writes its
output to 'traces.csv'.

The output of this script is an all lower case csv file with columns: workflow,
inputsize, task, machine, time.
'''
if __name__ == '__main__':
    # read the data from the csv files
    NODES = ['asok01', 'asok02', 'c2', 'local', 'n1', 'n2']
    TRACE_FILES = [
        path.join('tasks_lotaru', f'tasks_lotaru_{node}.csv') for node in NODES]
    TRACE_HEADER = {
        'Machine':                   'string',
        'WorkflowNum':               'string',
        'Workflow':                  'string',
        'TaskName':                  'string',
        'Estimator':                 'string',
        'Feature':                   'string',
        'SizeInput':                 'int64',
        'Predicted':                 'float64',
        'Real':                      'int64',
        'Deviation':                 'float64',
        'TaskInputSize':             'int64',
        'WorkflowInputSize':         'int64',
        'rchar':                     'int64',
        'wchar':                     'int64',
        'PeakRSS':                   'int64',
        'CPUAssigned':               'int64',
        'CPUUsed':                   'float64',
    }
    data = ','.join(TRACE_HEADER.keys())
    for filename in TRACE_FILES:
        with open(filename) as file:
            data += '\n' + '\n'.join(file.readlines()[1:])
    df = pd.read_csv(StringIO(data.lower()), dtype=TRACE_HEADER)

    # normalize the data and write it to the output file
    RENAME_COLUMNS = {
        'workflowinputsize': 'inputsize',
        'taskname': 'task',
        'real': 'time',
        'peakrss': 'memory',
    }
    INDEX_COLUMNS = ['workflow', 'task', 'machine']
    DATA_COLUMNS = ['wchar', 'taskinputsize',]
    df = df.rename(columns=RENAME_COLUMNS)
    print(df.columns)
    df = df[INDEX_COLUMNS + DATA_COLUMNS]
    grouped = df.groupby(INDEX_COLUMNS).agg(lambda col: np.unique(col)[0])
    df = grouped.reset_index()
    df.to_csv('traces.csv', index=False)
