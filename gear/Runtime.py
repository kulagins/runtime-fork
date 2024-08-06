import sys
import requests
import heapq
from scipy import stats
from gear.Constants import NODES, URL


class Task:
    def __init__(self, name, start_time, run_time, machine, memory):
        self.name = name
        self.start_time = start_time
        self.run_time = run_time
        self.machine = machine
        self.memory = memory

    def __lt__(self, other):
        return self.name < other.name


class Runtime:
    def __init__(self, wf, traces, cluster):
        self.wf = wf
        self.traces = traces
        self.task_data = self.get_task_data()
        self.cluster = cluster
        self.execution_id = None
        self.task_queue = None
        self.event_queue = None
        self.time = None
        self.free_mem = self.cluster.mem_dict.copy()

    def get_task_data(self):
        data = self.traces.copy()
        for task in self.wf.get_tasks():
            for node in NODES:
                if (task, node) not in data.index:
                    data.loc[(task, node), :] = [1, 5e7]

        # TODO tasks without traces have a 50/50 chance of having a run_time of
        # 0 predicted
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
                'machines': self.cluster.request_dict,
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
        j = r.json()
        return j['id'], j['schedule']

    def _api_update_wf(self):
        print('_api_update_wf not yet implemented', file=sys.stderr)
        exit(-1)

    def _create_task_queue(self, schedule):
        self.task_queue = []
        for task_name, v in schedule.items():
            start_time = v['start']
            machine = v['machine']
            run_time = self.task_data.loc[task_name, machine]['time']
            memory = self.task_data.loc[task_name, machine]['memory']
            task = Task(task_name, start_time, run_time, machine, memory)
            heapq.heappush(self.task_queue,
                           (start_time, self._start_task, task))

    def setup_simulation(self):
        id, schedule = self._api_register_wf()
        self.execution_id = id
        self._create_task_queue(schedule)
        self.event_queue = []
        self.time = 0

    def _next(self):
        while len(self.task_queue) + len(self.event_queue) > 0:
            # if one of the queues is empty pop from the other
            if len(self.task_queue) == 0:
                yield heapq.heappop(self.event_queue)
            elif len(self.event_queue) == 0:
                yield heapq.heappop(self.task_queue)
            elif self.task_queue[0][0] < self.event_queue[0][0]:
                yield heapq.heappop(self.task_queue)
            else:
                yield heapq.heappop(self.event_queue)

    def _start_task(self, task):
        print(f'{self.time}: starting task {task.name}')
        if not self.wf.task_is_ready(task.name):
            print('unable to start task with unfulfilled dependencies',
                  file=sys.stderr)
            exit(-1)
        if self.free_mem[task.machine] < task.memory:
            # TODO maybe try to wait for some time?
            self._api_update_wf()
            return
        self.free_mem[task.machine] -= task.memory
        heapq.heappush(self.event_queue, (self.time + task.run_time,
                                          self._finish_task, task))

    def _finish_task(self, task):
        print(f'{self.time}: finishing task {task.name}')
        self.free_mem[task.machine] += task.memory

    def run_simulation(self):
        print('starting simulation')
        for t, f, args in self._next():
            # if self.time < t:
            # print(f'{self.time}: status: {self.free_mem}')
            self.time = t
            f(args)
        if not self.wf.workflow_is_finished():
            print('simulation finished but not all workflow tasks are done',
                  file=sys.stderr)
            exit(-1)
        print('finished simulation')
