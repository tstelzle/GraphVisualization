# Graph Visualization

This implements various Python classes to represent and visualize graphs.

## Improved Walker Algorithm

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

## Sugiyama Algorithm

The implementation of the Sugiyama algorithm can be run in the following way.

The algorithm uses the follwing steps

1. Edge-Reversal: Greedy Cycle Removal
2. Layering: Longest Path
3. Reduction of Edgeinterferences: Global Stifting
4. Determining the second coordinate: Algorithm Of Brandes And Köpf
5. Using the original edges for drawing

#### Newick Files

```shell
python main.py -sn
```

#### Graphml Files

```shell
python main.py -sg
```

## Required Libraries

The required libraries can be seen within the 'requirements.txt'.