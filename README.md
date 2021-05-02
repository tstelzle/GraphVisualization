# Graph Visualization

This implements various Python classes to represent and visualize graphs.

## Running

There are several possible parameters with which the main can be run.

### Parameter For Own Graph Representation

Hereby the filename to graph representation in adjacent list should be passed.

The file should be a new line for each node.
Behind the node name each node name there should be a colon.
Following the colon there should be a list of nodes to which the node has edges.
These edges should be separated by commas.

The parameter should be specified with the syntax '-o='

#### Example
```shell
python main.py -o=graph_1.txt
```

### Parameter For Drawing Graphml Files

The example graphs for the graphml file can all be parsed and drawn by passing the single parameter '-g'

#### Example

```shell
python main.py -g
```

### Parameter For Drawing Newick Format Files

Analogous to the graphml files the newick format files in the directed_graph_examples can be parsed and drawn with networkx.
Therefore, the parameter '-n' is passed to the python script.

#### Example

```shell
python main.py -n
```

### Improved Walker Algorithm

For drawing the example graphs an implementation of the improved Walker Algorithm can be used.

Therefore the following parameters are specified.

#### Newick Files

```shell
python main.py -wn
```

#### Graphml Files

```shell
python main.py -wg
```

## Required Libraries

The required libraries can be seen within the 'requirements.txt'.