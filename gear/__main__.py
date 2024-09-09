import argparse
import sys
import json
from .constants import URL
from .trace_reader import get_workflow_input_sizes, get_workflow
from .simulation import Simulation
from .cluster import Cluster, Machine
from .scheduler_connector import SchedulerConnector
from .runtime import Runtime, WorkflowState
# TODO check somewhere that constants and traces actually match


def choose_from_list(choices):
    for i, item in enumerate(choices):
        print(f'({i}) {item}')
    choice = None
    while choice is None:
        c = sys.stdin.readline()[0]
        try:
            i = int(c)
            choice = choices[i]
        except (ValueError, IndexError):
            print('invalid choice')
    return choice


def get_wf():
    wf_inputsizes_map = get_workflow_input_sizes()
    print('choose a workflow:')
    workflow = choose_from_list(list(wf_inputsizes_map.keys()))
    print('choose an input size')
    inputsize = choose_from_list(wf_inputsizes_map[workflow])
    return workflow, inputsize


if __name__ == '__main__':
    # parse command line
    parser = argparse.ArgumentParser(
        prog='python -m gear',
        description='runtime for b1-coop')
    parser.add_argument('-i', '--interactive',
                        action='store_true', default=False)
    parser.add_argument('-w', '--workflow', default=None)
    parser.add_argument('-a', '--algorithm', default='3')
    parser.add_argument('-m', '--machine', action='append')
    parser.add_argument('-e', '--add-error',
                        action='store_true', default=False)
    args = parser.parse_args(sys.argv[1:])
    if args.machine is None:
        args.machine = ['300:3200:5']
    # load workflow (i.e. list of task instances) from traces
    if args.interactive:
        workflow, inputsize = get_wf()
    elif args.workflow is not None:
        workflow, inputsize = args.workflow.split(':')
        inputsize = int(inputsize)
    else:
        parser.print_help()
        exit(-1)
    tasks = get_workflow(workflow, inputsize)
    # setup and start simulation
    simulation = Simulation()
    machines = {}
    id = 0
    for m in args.machine:
        m = m.split(':')
        speed = m[0]
        memory = m[1]
        count = 1
        if len(m) == 3:
            count = int(m[2])
        for _ in range(count):
            machines[id] = Machine(id, int(speed), int(memory)*int(1e6))
            id += 1
    cluster = Cluster(simulation, machines)
    scheduler_connector = SchedulerConnector(URL, int(args.algorithm))
    runtime = Runtime(workflow, tasks, simulation,
                      cluster, scheduler_connector, args.add_error)
    runtime.start_workflow()
    while runtime.state is WorkflowState.RUNNING:
        simulation.next_event()
    # save logs
    task_data = []
    for task in tasks.values():
        t = {
            'name': task.name,
            'machine': task.machine,
            'start': task.start_time,
            'finish': task.finish_time,
            'memory': task.memory,
        }
        task_data.append(t)
    save_data = {
        'workflow': workflow,
        'makespan': simulation.time,
        'tasks': task_data,
        'failed': runtime.task_fails,
    }
    h = hex(hash('seed')).split('x')[1][:7]
    with open(f'{workflow}-{inputsize}-{h}.log', 'w') as file:
        file.write(json.dumps(save_data, indent=3))
