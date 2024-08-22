from scipy import stats
from gear.TaskInstance import TaskInstance
from gear.Exceptions import TaskNotReadyException

# TODO improve separation of concern:
# should the task predictions really live in the workflow instance?
# should all the task trace data really live in the workflow instance?
# should the workflow instance object really have a reference to the cluster?
# should the workflow instance really allocate and free memory on the cluster?


class WorkflowInstance:
    def __init__(self, wf, traces, cluster):
        self.wf = wf
        self.cluster = cluster
        self.task_data = self._prepare_data(traces)
        self.tasks = {}

    def _prepare_data(self, traces):
        # fill in tasks without traces
        for task in self.wf.get_tasks():
            for machine in self.cluster:
                if (task, machine) not in traces.index:
                    traces.loc[(task, machine), :] = [1, 5e7]
        # calculate predicted value for time and memory for each task
        def predict(value): return int(
            stats.norm(loc=value, scale=0.1*value).rvs())
        traces['time_predicted'] = traces['time'].apply(predict)
        traces['memory_predicted'] = traces['memory'].apply(predict)
        # all tasks with a run time of 1 (for example the ones without traces
        # we filled in above) have a 50% chance of having a predicted runtime
        # of 0. a predicted runtime of 0 leads to incorrect schedules.
        traces.loc[traces['time_predicted'] == 0, 'time_predicted'] = 1
        return traces
        self.task_data = traces[['time', 'memory']]

    def get_name(self):
        return self.wf.name

    def get_task_predictions(self):
        df = self.task_data[['time_predicted', 'memory_predicted']]
        return {key[0]: df.loc[key[0]].to_dict() for key in df.index}

    def start_task(self, task_name, machine, current_time):
        assert task_name not in self.tasks
        run_time = self.task_data.loc[(task_name, machine), 'time']
        memory = self.task_data.loc[(task_name, machine), 'memory']
        for dep in self.wf.get_deps(task_name):
            if dep not in self.tasks or not self.tasks[dep].done:
                raise TaskNotReadyException()
        # alloc_mem may throw an exception
        # this pattern can be used to re-raise an exception
        # might be useful if I want to partially handle the exception here for
        # retries but still propagate it to the runtime
        # try:
        #    do_something_dangerous()
        # except:
        #    do_something_to_apologize()
        #    raise
        self.cluster.alloc_mem(machine, memory)
        self.tasks[task_name] = TaskInstance(task_name, current_time, run_time,
                                             machine, memory)
        return self.tasks[task_name]

    def finish_task(self, task_name):
        task = self.tasks[task_name]
        task.done = True
        task.running = False
        self.cluster.free_mem(task.machine, task.memory)

    def get_finished_tasks(self):
        return [name for name, task in self.tasks.items() if task.done]

    def get_running_tasks(self):
        ret = {}
        for name, task in self.tasks.items():
            if task.running:
                ret[name] = {
                    'start_time': task.start_time,
                    'memory': task.memory,
                }
        return ret
