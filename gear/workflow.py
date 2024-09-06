from enum import Enum, auto


class TaskState(Enum):
    # CREATED = auto()
    BLOCKED = auto()
    READY = auto()
    RUNNING = auto()
    DONE = auto()
    # FAILED = auto()


class Task:
    '''
    A Task object that is created by the trace_reader, passed to the runtime
    and shared with the scheduler and cluster.

    The work field is used to determine run by dividing the work through a
    machine's speed.

    We do not make a distinction between abstract task and task instance.
    '''

    def __init__(self, name, parents, work, memory):
        self.name = name
        self.parents = parents
        self.work = work
        self.memory = memory
        self.machine = None
        self.start_time = None
        self.finish_time = None
        self.state = TaskState.BLOCKED
