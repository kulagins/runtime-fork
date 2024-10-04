from enum import Enum, auto
from .exceptions import (
    TaskNotReadyException,
    InsufficientMemoryException,
    MachineInUseException,
)
from .simulation import Event
from .workflow import TaskState
# TODO predictor class and option to turn off

"""
class WorkflowState(Enum):
    CREATED = auto()
    RUNNING = auto()
    DONE = auto()
    # FAILED = auto()


class Runtime:
    def __init__(self, wf_name, tasks, simulation, cluster, scheduler_connector, add_error):
        self.wf_name = wf_name
        self.tasks = tasks
        self.simulation = simulation
        self.cluster = cluster
        self.scheduler_connector = scheduler_connector
        self.cluster.register_task_finish_cb(self.operate)
        self.state = WorkflowState.CREATED
        self.task_fails = []
        self.add_error = add_error

    def start_workflow(self):
        task_data = [{'name': t.name, 'work': t.work, 'memory': t.memory, 'wchar': t.wchar, 'taskinputsize': t.taskinputsize }
                     for t in self.tasks.values()]
        if self.add_error:
            task_data = [{'name': t.name, 'work': t.work_predicted, 'memory': t.memory_predicted, 'wchar': t.wchar, 'taskinputsize': t.taskinputsize}
                         for t in self.tasks.values()]
        print(self.wf_name)
        schedule = self.scheduler_connector.register_wf(
            self.wf_name,
            task_data,
            self.cluster.get_cluster_info(),
        )
        self.load_schedule(schedule)
        self.state = WorkflowState.RUNNING
        self.operate()

    def start_task(self, task, tags):
        try:
            self.cluster.start_task(task)
        except (TaskNotReadyException, InsufficientMemoryException, MachineInUseException) as e:
            self.task_fails.append({
                'time': self.simulation.time,
                'task': task.name,
                'machine': task.machine,
                'reason': type(e).__name__,
                'occupied by ': str(e.args[1]),
                'expected runtime ': task.work_predicted,
                'actual runtime ': task.work,
                'expected memory usage ':task.memory_predicted,
                'actual memory usage': task.memory
            })
            if('repeat' in tags):
                print("task "+task.name+" already repeated, erroring")
                self.simulation.reset_queue(tag='schedule')

                schedule = self.scheduler_connector.update_wf(
                    self.simulation.time,
                    type(e).__name__ +": "+ e.args[0]+" occupied by "+ str(e.args[1])+" on machine "+ str(e.args[2]),
                    [t.name for t in self.tasks.values() if t.state == TaskState.DONE],
                    [{'name': t.name, 'start': t.start_time, 'machine': t.machine}
                     for t in self.tasks.values() if t.state == TaskState.RUNNING]
                )
                self.load_schedule(schedule)
            else:
                print("try to repeat task "+task.name)
                blockingEvent = self.simulation.find_event(e.args[1])
                newFinishTime = self.simulation.time
                if blockingEvent==None:
                    print("No event found for task "+str(e.args[1])+" error "+ type(e).__name__ )
                    newFinishTime += (task.work_predicted / task.machineSpeed) * 0.1
                else:
                    newFinishTime = blockingEvent.data.start_time + blockingEvent.data.work / blockingEvent.data.machineSpeed
                self.simulation.add_event(Event(
                    newFinishTime,
                    self.start_task,
                    task,
                    tags=['schedule', 'repeat'],
                ))

    def load_schedule(self, schedule):
        for item in schedule:
            task = self.tasks['"'+item['task']+'"']
            task.machine = item['machine']

            machines_with_my_id = {key: machine for key, machine in  self.cluster.machines.items() if machine.id == task.machine}
            assert (len(machines_with_my_id)==1)
            task.machineSpeed= (list(machines_with_my_id.values())[0]).speed
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
"""