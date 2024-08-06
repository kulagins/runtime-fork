import pandas as pd


class Cluster:
    def __init__(self, node_file):
        self.node_file = node_file
        data = pd.read_csv(node_file, index_col='machine',
                           usecols=['machine', 'memory'])
        data['memory'] = data['memory'].apply(lambda x: int(x * 1e9))
        self.request_dict = data.to_dict('index')
        self.mem_dict = data.to_dict()['memory']
