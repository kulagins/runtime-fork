from enum import Enum, auto
from .exceptions import (
    TaskNotReadyException,
    InsufficientMemoryException,
    MachineInUseException,
)
from .simulation import Event
from .workflow import TaskState
# TODO predictor class and option to turn off


class WorkflowState(Enum):
    CREATED = auto()
    RUNNING = auto()
    DONE = auto()
    # FAILED = auto()


class Runtime:
    def __init__(self, wf_name, tasks, simulation, cluster, scheduler_connector):
        self.wf_name = wf_name
        self.tasks = tasks
        self.simulation = simulation
        self.cluster = cluster
        self.scheduler_connector = scheduler_connector
        self.cluster.register_task_finish_cb(self.operate)
        self.state = WorkflowState.CREATED
        self.task_fails = []

    def start_workflow(self):
        schedule = self.scheduler_connector.register_wf(
            self.wf_name,
            [{'name': t.name, 'work': t.work, 'memory': t.memory}
                for t in self.tasks.values()],
            # self.wf_instance.get_task_predictions(),
            self.cluster.get_cluster_info(),
        )
        self.load_schedule(schedule)
        self.state = WorkflowState.RUNNING
        self.operate()

    def start_task(self, task):
        try:
            self.cluster.start_task(task)
        except (TaskNotReadyException, InsufficientMemoryException, MachineInUseException) as e:
            self.task_fails.append({
                'time': self.simulation.time,
                'task': task.name,
                'machine': task.machine,
                'reason': type(e).__name__
            })
            self.simulation.reset_queue(tag='schedule')
            schedule = self.scheduler_connector.update_wf(
                self.simulation.time,
                type(e).__name__,
                [t.name for t in self.tasks.values() if t.state == TaskState.DONE],
                [{'name': t.name, 'start': t.start_time, 'machine': t.machine}
                 for t in self.tasks.values() if t.state == TaskState.RUNNING]
            )
            self.load_schedule(schedule)

    def load_schedule(self, schedule):
        for item in schedule:
            task = self.tasks[item['task']]
            task.machine = item['machine']
            self.simulation.add_event(Event(
                item['start'],
                self.start_task,
                task,
                tags=['schedule'],
            ))

    def operate(self):
        if len(self.get_tasks(TaskState.DONE)) == len(self.get_tasks()):
            self.state = WorkflowState.DONE
            return
        for task in self.get_tasks(TaskState.BLOCKED):
            task.state = TaskState.READY
            for parent in task.parents:
                if self.tasks[parent].state is not TaskState.DONE:
                    task.state = TaskState.BLOCKED
                    break

    def get_tasks(self, task_state=None):
        if task_state is None:
            return self.tasks.values()
        return [t for t in self.tasks.values() if t.state == task_state]
