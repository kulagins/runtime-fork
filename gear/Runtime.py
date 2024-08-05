import sys
import requests
import heapq
from scipy import stats
from gear.Constants import NODES, URL
from gear.Cluster import get_machine_info


class Runtime:
    def __init__(self, wf, traces):
        self.wf = wf
        self.traces = traces
        self.task_data = self.get_task_data()
        self.execution_name = None
        self.task_queue = None
        self.event_queue = None
        self.time = None
        self.finished = None

    def get_task_data(self):
        data = self.traces.copy()
        for task in self.wf.get_tasks():
            for node in NODES:
                if (task, node) not in data.index:
                    data.loc[(task, node), :] = [1, 5e7]

        def predict(value): return int(
            stats.norm(loc=value, scale=0.1*value).rvs())
        data['time_predicted'] = data['time'].apply(predict)
        data['memory_predicted'] = data['memory'].apply(predict)
        return data

    def create_new_wf_request(self):
        # construct task data dict
        df = self.task_data[['time_predicted', 'memory_predicted']]
        task_data = {key[0]: df.loc[key[0]].to_dict() for key in df.index}
        # construct final dict
        # TODO make algorithm configurable via cli
        data = {
            'algorithm': 1,
            'workflow': {
                'name': self.wf.name,
                'tasks': task_data,
            },
            'cluster': {
                'machines': get_machine_info(),
            },
        }
        return data

    def _api_register_wf(self):
        data = self.create_new_wf_request()
        try:
            r = requests.post(f'{URL}/wf/new', json=data, timeout=1)
        except requests.ConnectionError:
            print('error connecting to scheduler', file=sys.stderr)
            exit(-1)
        if not r.status_code == 200:
            print('Unable to register workflow. Server returned:', file=sys.stderr)
            print(r.status_code, r.text, file=sys.stderr)
            exit(-1)
        # TODO construct task_queue from response
        return None

    def _api_update_wf(self):
        None

    def setup_simulation(self):
        name, queue = self._api_register_wf()
        self.execution_name = name
        self.task_queue = queue
        self.event_queue = []
        self.time = 0
        self.finished = False

    def run_simulation(self):
        while not self.finished:
            if len(self.task_queue) > 0:
                for task in self.task_queue:
                    # TODO start task, store events in event_queue, if
                    # unsuccessful store in updates
                    heapq.heappush(self.event_queue, (2, None))
                    None
                self._api_update_wf()
            elif len(self.event_queue) > 0:
                _ = heapq.heappop(self.event_queue)
                # TODO execute event
                self._api_update_wf()
            else:
                self.finished = True
