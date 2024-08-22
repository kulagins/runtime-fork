import heapq
from gear.Exceptions import TaskNotReadyException, InsufficientMemoryException
from gear.WorkflowInstance import WorkflowInstance
from gear.MultiQ import MultiQ, MultiQItem
from gear.Constants import NODES


class Runtime:
    def __init__(self, wf, traces, cluster, scheduler_connector):
        self.wf_instance = WorkflowInstance(wf, traces, cluster)
        self.cluster = cluster
        self.scheduler_connector = scheduler_connector
        self.multiq = MultiQ()
        # TODO remove the following?
        self.time = None
        self.free_mem = None
        self.running_tasks = None

    def setup_simulation(self):
        schedule = self.scheduler_connector.register_wf(
            self.wf_instance.get_name(),
            self.wf_instance.get_task_predictions(),
            self.cluster.get_cluster_info())
        schedule_queue = self._create_schedule_queue(schedule)
        self.multiq.add_queue("start", queue=schedule_queue, priority=10)
        self.multiq.add_queue("finish", priority=1)
        self.time = 0

    def _create_schedule_queue(self, schedule):
        queue = []
        for task_name, v in schedule.items():
            task_name = task_name.lower()
            start_time = v['start']
            # TODO remove
            if type(v['machine']) is int:
                machine = NODES[v['machine']]
            else:
                machine = v['machine']
            heapq.heappush(queue, MultiQItem(
                start_time, self._start_task, (task_name, machine)))
        return queue

    def run_simulation(self):
        print('starting simulation')
        for time, func, args in self.multiq:
            self.time = time
            func(*args)
        # TODO check that workflow is acutally done
        print('finished simulation')

    def _start_task(self, task_name, machine):
        print(f'{self.time}: starting task {task_name}')
        try:
            task = self.wf_instance.start_task(task_name, machine, self.time)
        except (TaskNotReadyException, InsufficientMemoryException):
            print('unable to start task: requesting updated schedule')
            self._handle_error()
            return
        self.multiq.push_to_queue('finish', MultiQItem(
            self.time + task.run_time, self._finish_task, (task_name,)))

    def _finish_task(self, task_name):
        print(f'{self.time}: finishing task {task_name}')
        self.wf_instance.finish_task(task_name)

    def _handle_error(self):
        schedule = self.scheduler_connector.update_wf(
            self.wf_instance.get_finished_tasks(),
            self.wf_instance.get_running_tasks(),
        )
        self._create_schedule_queue(schedule)
        self.failed_task = None
