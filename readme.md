# gear - b1-coop runtime

This repository contains code for simulating workflow executions on
heterogenous clusters. The repository is structured as follows:

 - `data/traces.csv` contains execution traces for several workflows
 - `data/machines.csv` contains descriptions for the simulated machines
 - `data/workflows/` contains workflow descriptions in the dot file format
 - `gear/` contains the code for the simulation
 - `contrib/prepare_traces.py` contains a small script to generate the
   `traces.csv` file from the `tasks_lotaru.zip` file

## Installing

Assuming a unix system with a posix shell environment and python including
python-venv and pip installed: Executing the following commands clones the
repository into `./gear` and prepares everything to run the simulation:

```
git clone https://github.com/belapaulus/gear.git
cd gear 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the simulation

Assuming that the scheduler (not part of this repository) is running, you can
run a simulation with `python -m gear -i` from within the repository.

Alternatively the workflow and workflow input size can be specified via
`-w <workflow>:<input_size>`.

The cluster can be changed by specifing machines with
`-m <speed>:<memory in MiB>:<count>`. For example the following command line
would simulate the workflow atacseq with an input size of 2223941232 bytes on
a cluster with three machines with a speed of 300 and 32GiB memory and two
machines with a speed of 400 and 64GiB memory.

`python -m gear -w atacseq:2223941232 -m 300:3200:3 -m 400:6400:2`

For now available workflow input sizes can only be listed in interactive mode.

## Architecture

The simulation is built around the main event queue component. An event in the
simulation is just a function associated with a time and some data. Events can
be added to the event queue. A call to next_event() executes the next event.

Running the simulation involves the following:

 - first a workflow is chosen
 - loading the workflow from the traces gives the simulation a list of tasks
   to execute
 - the simulation object is created
 - a cluster object is created from a list of machines and the cluster object
   receives a reference to the simulation so it can register its events
 - the scheduler connector object is created. The scheduler connector talks
   via the REST API to the dynamic scheduler
 - the runtime is instantiated with references to the tasks, cluster, scheduler
   connector and simulation
 - the runtime starts the workflow by requesting a schedule from the scheduler
   connector and adding all start task events to the event queue
 - the main simulation loop keeps executing events until the workflow is
   finished
 - once the workflow is finished the logs are exported to a file

The main events are start and finish task events. The start task event calls
the start task function in the runtime which in turn tells the cluster to start
the given task. If that is succesful the cluster registers a finish task event
which calls the cluster to free the resources, which in turn calls back to the
runtime to update the task states. If the cluster cannot start a task an
exception is raised and the runtime requests an updated schedule.

## Simulation-Scheduler API

The simulated runtime and scheduler communicate via a REST API. The scheduler
implements the REST server to which the runtime makes requests. There are
only two types of requests:

 - `/wf/new`: to register a new workflow execution
 - `/wf/<id>/update`: to communicate if the schedule needs to be updated

### Registering a New Workflow Execution

To register a new workflow execution, the simulated runtime makes a single
POST request to `/wf/new`. The request body contains information about the
workflow and cluster. The response shall contain the id for the newly
registered workflow as well as a complete schedule.

The information about the workflow structure and cluster resources is
transmitted as a single json of the following format:

```
{
    "algorithm": <algorithm_number>,
    "workflow": {
        "name": "<workflow_name>",
        "tasks": [
            {
                "name": "<task_name",
                "work": "<work_predicted>",
                "memory": "<memory_predicted>"
            },
            ...
        ]
    },
    "cluster": {
        "machines": [
            {
                "id": <id>,
                "memory": <memory>,
                "speed": <speed>
            },
            ...
        ]
    }
}
```

The scheduler shall reply to this request with the schedule in json of the
following format:

```
{
    "id": <workflow_id>,
    "schedule": [
        {
            "task": <task_name>,
            "start": <start_time>,
            "machine": <machine>
        },
        ...
    ]
}
```

### Requesting an Updated Schedule

In case the runtime can not fulfill the schedule it received, it can make a
POST request to `/wf/<id>/update` to request an updated schedule. The request
body contains information about the current workflow execution status as json
in the following format:

```
{
    "time": <time>,
    "finished_tasks": ["<task_1>", "task_2", ...],
    "running_tasks": [
        {
            "name": <task_name>,
            "start_time": <start_time>,
            "memory": <memory>
        },
        ...
    ]
}
```

The scheduler shall reply to this request with an updated schedule in json of
the following format:

```
{
    "schedule": [
        {
            "task": <task_name>,
            "start": <start_time>,
            "machine": <machine>
        },
        ...
    ]
}
```
