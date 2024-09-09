from .exceptions import (
    InsufficientMemoryException,
    MachineInUseException,
    TaskNotReadyException,
)
from .workflow import TaskState
from .simulation import Event


class Machine:
    def __init__(self, id, speed, memory):
        # TODO change name to id
        self.id = id
        self.speed = speed
        self.memory_total = memory
        self.memory_available = memory
        self.in_use = False


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
            raise TaskNotReadyException
        machine = self.machines[task.machine]
        if machine.in_use:
            raise MachineInUseException
        if task.memory > machine.memory_available:
            raise InsufficientMemoryException
        machine.memory_available -= task.memory
        machine.in_use = True
        task.start_time = self.simulation.time
        task.state = TaskState.RUNNING
        finish_time = self.simulation.time + (task.work / machine.speed)
        self.simulation.add_event(
            Event(finish_time, self.finish_task, task, priority=1))

    def finish_task(self, task):
        machine = self.machines[task.machine]
        assert machine.memory_available + task.memory <= machine.memory_total
        assert machine.in_use
        machine.memory_available += task.memory
        machine.in_use = False
        task.finish_time = self.simulation.time
        task.state = TaskState.DONE
        self.task_finish_cb()

    def register_task_finish_cb(self, callback):
        self.task_finish_cb = callback
