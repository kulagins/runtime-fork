

# TODO support multiple instances per task
# TODO support retries
# TODO is it really a good choice to have separate booleans for the state?
# TODO should the task be set to running by default?
class TaskInstance:
    def __init__(self, name, start_time, run_time, machine, memory):
        self.name = name
        self.machine = machine
        self.start_time = start_time
        self.run_time = run_time
        self.memory = memory
        self.running = True
        self.done = False
