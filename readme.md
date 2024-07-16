# gear - b1-coop runtime

This repository contains a program for simulating workflow executions on
heterogenous clusters. The repository is structured as follows:

 - 'data/traces.csv' contains execution traces for several workflows
 - 'data/nodes.csv' contains descriptions for the simulated nodes
 - 'data/workflows/' contains workflow descriptions in the dot file format
 - 'gear/' contains the code
 - 'contrib/prepare_traces.py' contains a small script to generate the
   'traces.csv' file from the 'tasks_lotaru.zip' file

## todo

 - test run all worfklows and input sizes
 - fix networkx bug
