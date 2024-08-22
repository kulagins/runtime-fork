import argparse
import sys
from gear.Cluster import Cluster
from gear.Constants import NODE_FILE, WF_DOT_FILE_MAP, WORKFLOWS, URL
from gear.Runtime import Runtime
from gear.SchedulerConnector import SchedulerConnector
from gear.TraceReader import TraceReader
from gear.Workflow import Workflow


def getch():
    return sys.stdin.readline()[0]


class Cli:
    def __init__(self):
        self.tr = TraceReader()
        self.wf_inputsizes_map = self.tr.get_workflow_inputsizes_map()

    def get_wf(self):
        print('choose a workflow:')
        for i in range(len(WORKFLOWS)):
            print(f'({i}) {WORKFLOWS[i]}')
        workflow = None
        while workflow is None:
            c = getch()
            try:
                i = int(c)
                workflow = WORKFLOWS[i]
            except (ValueError, IndexError):
                print('invalid workflow number')
        print('choose an input size')
        inputsizes = self.wf_inputsizes_map[workflow]
        for i in range(len(inputsizes)):
            print(f'({i}) {inputsizes[i]}')
        inputsize = None
        while inputsize is None:
            c = getch()
            try:
                i = int(c)
                inputsize = inputsizes[i]
            except (ValueError, IndexError):
                print('invalid input size number')
        return workflow, inputsize

    def start(self, argv):
        # TODO add proper logging
        workflow_options = []
        for k, v in self.wf_inputsizes_map.items():
            for size in v:
                workflow_options.append(f'{k}:{size}')

        parser = argparse.ArgumentParser(
            prog='python -m gear',
            description='runtime for b1-coop')
        parser.add_argument('-i', '--interactive', action='store_true',
                            default=False)
        parser.add_argument('-w', '--workflow', default=None,
                            choices=workflow_options)
        args = parser.parse_args(argv)

        if args.interactive:
            workflow, inputsize = self.get_wf()
        elif args.workflow is not None:
            workflow, inputsize = args.workflow.split(':')
            inputsize = int(inputsize)
        else:
            parser.print_help()
            exit(-1)

        wf = Workflow(workflow, WF_DOT_FILE_MAP[workflow])
        traces = self.tr.get_traces(workflow, inputsize)
        cluster = Cluster(NODE_FILE)
        scheduler_connector = SchedulerConnector(URL)
        runtime = Runtime(wf, traces, cluster, scheduler_connector)
        runtime.setup_simulation()
        runtime.run_simulation()
