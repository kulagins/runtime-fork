# gear - b1-coop runtime

This repository contains a program for simulating workflow executions on
heterogenous clusters. The repository is structured as follows:

 - `data/traces.csv` contains execution traces for several workflows
 - `data/nodes.csv` contains descriptions for the simulated nodes
 - `data/workflows/` contains workflow descriptions in the dot file format
 - `gear/` contains the code for the simulation
 - `contrib/prepare_traces.py` contains a small script to generate the
   `traces.csv` file from the `tasks_lotaru.zip` file

## Installing

Assuming a unix system with a posix shell environment and python including
python-venv and pip installed: Executing the following commands clones the
repository into `./b1-coop` and prepares everything to run the simulation:

```
git clone https://github.com/belapaulus/b1-coop.git
cd b1-coop
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the simulation

Assuming that the scheduler (not part of this repository) is running, you can
run a simulation with `python -m gear -i` from within the repository.

## Simulation-Scheduler API

The simulated runtime and scheduler communicate via a REST API. The scheduler
implements the REST server to which the runtime makes requests. There are
only two types of requests:

 - `/wf/new`: to register a new workflow execution
 - `/wf/<id>/update`: to communicate if the schedule needs to be updated

### Registering a new Workflow

To register a new workflow execution, the simulated runtime makes a single
POST request to `/wf/new`. The request body contains information about the
workflow structure and cluster resources. The response shall contain the id
for the newly registered workflow as well as a complete schedule.

The information about the workflow structure and cluster resources is
transmitted as a single json of the following format:

```
{
    "workflow": {
        "tasks": {
            "<task_name>": {
                "time_predicted": {
                    "<node_1>": <time_predicted>,
                    ...
                },
                "memory_predicted": {
                    "<node_1>": <memory_predicted>,
                    ...
                }
            },
            ...
        },
        "dependencies": {
            "<task_name>": [<dependency>, <dependency>, ...],
            ...
        }
    },
    "cluster": {
        "machines": {
            "<machine_name>": {
                "memory": <memory>
            },
            ...
        }
    }
}
```

The simulated runtime prints the new workflow request instead of sending it, if
the `-p` option is specified.

The scheduler shall reply to this request with the schedule in json of the
following format:

```
{
    "id": <workflow_id>,
    "schedule": {
        "<task_name">: {
            "start": <start_time>,
            "machine": <machine>
        },
        ...
    }
}
```

### Requesting an Updated Schedule

// TODO

## TODO

 - specify interface to update schedule
 - why is time_predicted sometimes 0
 - test run all worfklows and input sizes
 - fix networkx bug
 - improve help output
