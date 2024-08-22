import pandas as pd
from gear.Constants import TRACE_FILE, TRACE_HEADER

# TODO potentially move prepare data from workflow instance to trace reader


class TraceReader:
    def __init__(self):
        df = pd.read_csv(TRACE_FILE, dtype=TRACE_HEADER)
        self.data = df.set_index(['workflow', 'inputsize', 'task', 'machine'])
        self.workflows = df['workflow'].unique()
        self.workflow_inputsizes_map = {}
        for wf in self.workflows:
            self.workflow_inputsizes_map[wf] = list(
                df[df['workflow'] == wf]['inputsize'].unique())

    def get_workflow_inputsizes_map(self):
        return self.workflow_inputsizes_map

    def get_traces(self, workflow, inputsize):
        return self.data.loc[workflow, inputsize]
