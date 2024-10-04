from .exceptions import (
    InsufficientMemoryException,
    MachineInUseException,
    TaskNotReadyException, TookMuchLess,
)
from .workflow import TaskState
from .simulation import Event
from .constants import THRESHOLD

class Machine:
    def __init__(self, id, speed, memory):
        # TODO change name to id
        self.id = id
        self.speed = speed
        self.memory_total = memory
        self.memory_available = memory
        self.in_use = False
        self.taskName = ""


class Cluster:
    def __init__(self, simulation, machines):
        self.simulation = simulation
        self.machines = machines
        self.task_finish_cb = None

    def get_cluster_info(self):
        return [{'id': m.id, 'memory': m.memory_total, 'speed': m.speed} for m in self.machines.values()]

    def start_task(self, task):
        assert task.state is not TaskState.DONE
        assert task.state is not TaskState.RUNNING
        if task.state is TaskState.BLOCKED:
            raise TaskNotReadyException(task.name, task.parents,-1)
        machine = self.machines[task.machine]
        if machine.in_use:
            raise MachineInUseException(task.name, machine.taskName, machine.id)
        if task.memory > machine.memory_available:
            raise InsufficientMemoryException(task.name, "", machine.id)
        machine.memory_available -= task.memory
        machine.in_use = True
        machine.taskName=task.name
        task.start_time = self.simulation.time
        task.state = TaskState.RUNNING


    def finish_task(self, task):
        machine = self.machines[task.machine]
        assert machine.memory_available + task.memory <= machine.memory_total
        assert machine.in_use
        machine.memory_available += task.memory
        machine.in_use = False
        machine.taskName=""
        task.finish_time = self.simulation.time
        task.state = TaskState.DONE
        self.task_finish_cb()
        if task.work_predicted > task.work * (1 + THRESHOLD):
          raise TookMuchLess(task.name, self.simulation.time, machine.id)

    def register_task_finish_cb(self, callback):
        self.task_finish_cb = callback
