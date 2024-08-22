import pandas as pd
from gear.Exceptions import InsufficientMemoryException


class Cluster:
    def __init__(self, node_file):
        self.data = pd.read_csv(node_file, index_col='machine',
                                usecols=['machine', 'memory', 'cpu_events'])
        self.data.rename(columns={'cpu_events': 'speed'})
        self.data['memory'] = self.data['memory'].apply(lambda x: int(x * 1e9))
        self.capacity = self.data.to_dict()['memory']
        self.available = self.capacity.copy()

    def get_cluster_info(self):
        return self.data.to_dict('index')

    def get_cluster_state(self):
        return self.available

    def alloc_mem(self, machine, memory):
        if memory > self.available[machine]:
            raise InsufficientMemoryException()
        self.available[machine] -= memory

    def free_mem(self, machine, memory):
        assert self.available[machine] + memory <= self.capacity[machine]
        self.available[machine] += memory

    def __iter__(self):
        return iter(self.data.index)
