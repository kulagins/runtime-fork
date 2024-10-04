from enum import Enum, auto
from .exceptions import (
    TaskNotReadyException,
    InsufficientMemoryException,
    MachineInUseException, TookMuchLess,
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
            finish_time = task.start_time + (task.work / self.cluster.machines[task.machine].speed)
            self.simulation.add_event(
                Event(finish_time, self.finish_task, task, priority=1))
        except MachineInUseException as e:
            self.task_fails.append({
                'time': self.simulation.time,
                'task': task.name,
                'machine': task.machine,
                'reason': type(e).__name__,
                'occupied by ': str(e.args[1]),
                'expected runtime ': task.work_predicted,
                'actual runtime ': task.work,
                'expected memory usage ': task.memory_predicted,
                'actual memory usage': task.memory
            })
            # if('repeat' in tags):
            # print("task "+task.name+" already repeated, erroring")
            self.simulation.reset_queue(tag='schedule')
            blockingEvent = self.simulation.find_event_by_name(e.args[1])
            if blockingEvent == None:
                newFinishTime = self.simulation.time
            else:
                newFinishTime = blockingEvent.data.start_time + blockingEvent.data.work / blockingEvent.data.machineSpeed
            schedule = self.scheduler_connector.update_wf(
                self.simulation.time,
                e.args[0],
                newFinishTime,
                type(e).__name__ + ": " + e.args[0] + " occupied by " + str(e.args[1]) + " on machine " + str(
                    e.args[2]),
                [t.name for t in self.tasks.values() if t.state == TaskState.DONE],
                [{'name': t.name, 'start': t.start_time, 'machine': t.machine, 'work': t.work}
                 for t in self.tasks.values() if t.state == TaskState.RUNNING]
            )
            self.load_schedule(schedule)
        except TaskNotReadyException as e:
            lastTimestampOfParentFinish=self.simulation.time
            criticalParent=None
            for parent in task.parents:
                parentEvent = self.simulation.find_event_by_name(parent)
                if parentEvent == None:
                    parentNoQ = parent.strip('"')
                    parentEvent = self.simulation.find_event_by_name(parentNoQ)
                    if parentEvent == None:
                        if len(task.parents)==1:
                            print("NO EVENT FOR PARENT "+parent)
                            parentTask = self.tasks [parent]
                            if parentTask.state!= TaskState.RUNNING:
                                task.state=TaskState.READY
                                self.start_task(task,tags)
                        else:
                            continue
                    else:
                        if parentEvent.data.state is TaskState.RUNNING:
                            realParentFinishTime = parentEvent.data.start_time + parentEvent.data.work / parentEvent.data.machineSpeed
                            if realParentFinishTime > lastTimestampOfParentFinish:
                                lastTimestampOfParentFinish = realParentFinishTime
                                criticalParent = parent
                else:
                    if parentEvent.data.state is TaskState.RUNNING:
                        realParentFinishTime = parentEvent.data.start_time + parentEvent.data.work / parentEvent.data.machineSpeed
                        if realParentFinishTime>lastTimestampOfParentFinish:
                            lastTimestampOfParentFinish= realParentFinishTime
                            criticalParent= parent

            self.simulation.reset_queue(tag='schedule')
            assert(task.name==e.args[0])
            schedule = self.scheduler_connector.update_wf(
                self.simulation.time,
                e.args[0],
                lastTimestampOfParentFinish,
                type(e).__name__ + ": " + e.args[0] + " occupied by " + ("noparent" if criticalParent==None else criticalParent) + " on machine " + str(
                    e.args[2]),
                [t.name for t in self.tasks.values() if t.state == TaskState.DONE],
                [{'name': t.name, 'start': t.start_time, 'machine': t.machine, 'work': t.work}
                 for t in self.tasks.values() if t.state == TaskState.RUNNING]
            )
            self.load_schedule(schedule)
        except InsufficientMemoryException as e:
            self.task_fails.append({
                'time': self.simulation.time,
                'task': task.name,
                'machine': task.machine,
                'reason': type(e).__name__,
                'occupied by ': str(e.args[1]),
                'expected runtime ': task.work_predicted,
                'actual runtime ': task.work,
                'expected memory usage ': task.memory_predicted,
                'actual memory usage': task.memory
            })
            self.simulation.reset_queue(tag='schedule')
            schedule = self.scheduler_connector.update_wf(
                self.simulation.time,
                e.args[0],
                self.simulation.time,
                type(e).__name__ + ": " + e.args[0] + " occupied by " + str(task.memory) + " on machine " + str(
                    e.args[2]),
                [t.name for t in self.tasks.values() if t.state == TaskState.DONE],
                [{'name': t.name, 'start': t.start_time, 'machine': t.machine, 'work': t.work}
                 for t in self.tasks.values() if t.state == TaskState.RUNNING]
            )
            self.load_schedule(schedule)
        except TookMuchLess as e:
            newFinishTime= e.args[1]
            self.simulation.reset_queue(tag='schedule')
            schedule = self.scheduler_connector.update_wf(
                self.simulation.time,
                e.args[0],
                newFinishTime,
                type(e).__name__ + ": " + e.args[0] + " occupied by " + "noparent" + " on machine " + str(
                    e.args[2]),
                [t.name for t in self.tasks.values() if t.state == TaskState.DONE],
                [{'name': t.name, 'start': t.start_time, 'machine': t.machine, 'work': t.work}
                 for t in self.tasks.values() if t.state == TaskState.RUNNING]
            )
            self.load_schedule(schedule)

    def finish_task(self, task, tags):
        try:
            self.cluster.finish_task(task)
        except TookMuchLess as e:
            newFinishTime = e.args[1]
            self.simulation.reset_queue(tag='schedule')
            schedule = self.scheduler_connector.update_wf(
                self.simulation.time,
                e.args[0],
                newFinishTime,
                type(e).__name__ + ": " + e.args[0] + " occupied by " + "noparent" + " on machine " + str(
                    e.args[2]),
                [t.name for t in self.tasks.values() if t.state == TaskState.DONE],
                [{'name': t.name, 'start': t.start_time, 'machine': t.machine, 'work': t.work}
                 for t in self.tasks.values() if t.state == TaskState.RUNNING]
            )
            self.load_schedule(schedule)
    def load_schedule(self, schedule):
        for item in schedule:
            if item['task'] == "graph_source" or item['task'] == "graph_target":
                continue
            else:
                try:
                    task = self.tasks[item['task']]
                except KeyError:
                    task = self.tasks['"' + item['task'] + '"']

                #task = self.tasks['"'+item['task']+'"']
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
