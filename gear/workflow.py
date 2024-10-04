from enum import Enum, auto
from scipy import stats


class TaskState(Enum):
    # CREATED = auto()
    BLOCKED = auto()
    READY = auto()
    RUNNING = auto()
    DONE = auto()
    # FAILED = auto()


def predict(value):
    rvs = stats.norm(loc=value, scale=0.1 * value).rvs()
    #if(abs(rvs-value)<0.1 * value):
   #     return value
   # else:
    return rvs


class Task:
    '''
    A Task object that is created by the trace_reader, passed to the runtime
    and shared with the scheduler and cluster.

    The work field is used to determine run by dividing the work through a
    machine's speed.

    We do not make a distinction between abstract task and task instance.
    '''

    def __init__(self, name, parents, work, memory, wchar, taskinputsize):
        self.name = name
        self.parents = parents
        self.work = work
        self.work_predicted = predict(work)
        self.memory = memory
        self.memory_predicted = predict(memory)
        self.wchar = wchar
        self.taskinputsize = taskinputsize
        self.machine = None
        self.machineSpeed=-1
        self.start_time = None
        self.finish_time = None
        self.state = TaskState.BLOCKED

    def __str__(self):
        return self.name
