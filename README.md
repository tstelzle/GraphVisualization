# Graph Visualization

This implements various Python classes to represent and visualize graphs.

When running "-h' on the main.py you can see a list of the options.

## Example Files

To run the specified algorithms on the Newick test files the option "-n" has to be added.
For the Graphml files "-g" has to be specified.

## Improved Walker Algorithm

For drawing the example graphs an implementation of the improved Walker Algorithm can be used.

Therefore the option "-w" should be added as option.

## Sugiyama Algorithm

The implementation of the Sugiyama algorithm can be run in the following way.

The algorithm uses the follwing steps

1. Edge-Reversal: Greedy Cycle Removal
2. Layering: Longest Path
3. Reduction of Edgeinterferences: Global Stifting
4. Determining the second coordinate: Algorithm Of Brandes And Köpf
5. Using the original edges for drawing

To run the sugiyama algorithm add the option "-sx".

The other option "-s" uses a graph data structure, which is self implemented and not by networks. 
There is an error in the remove_edges, hence this implementation is not working. 

## Tests

There are various self implemented tests (No Test Framework).
These can be run when the option "-t" is set.

## Required Libraries

The required libraries can be seen within the 'requirements.txt'.