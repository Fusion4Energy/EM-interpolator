# EM forces interpolator

## Quickstart

First, after downloading the package, install it using:

```
pip install .
```

After that, start the GUI using:

```
python -m em_interp
```

> **N.B.**  
> The first time you use the tool, it may take a long time to load. This is most likely due to C++ binding compilations from the GUI package. After this initial run, loading times should be much faster.
The first time you use the tool it will take a long time loading. This happens most likely due to C++ binding compilations from the GUI package. After this, the loading time should fall dramatically for next uses.

## GUI overview and functionalities
TODO

## Description of available algorithms

### KDTree neighbours

* K-Nearest: select the K closest mech nodes to the EM node
* Radius: select all mech nodes contained by a sphere of radius R centered on the EM node 

Two additional parameters are provided independently of the neighbour selection strategy:

* maximum distance cut-off: mech nodes farther than distance will be disregarded (more useful with k-nearest strategies)
* coincidence tolerance: distance at which a mech node and em node should be considered coincident.
In this case, no interpolation is called and the EM force is entirely assigned to the coincident mech node.

### Interpolation kernels

* Weight by distance: distribute the forces invertionally proportional to the distance from the EM node.
* FEM based: connect each mech node with a stiff beam to the EM node and distribute forces in order to have the same resultant force and a moment equal to zero.