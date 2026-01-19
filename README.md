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

## GUI overview and functionalities

The GUI is divided into two main tabs: the first is used to configure the interpoalation,
while the second is used to perform the interpolation, export data and check results.

### Configuration Tab
Three different paths must be indicated to run the interpolation:

- *EM folder*: path to a folder containing the EM forces. These are .csv files (with or without header, various separators are accepted) that must contain the coordinates of the EM centroids (in meters) and the EM forces to be interpolated (in Newton). The GUI allows to indicate which is the index (starting from 0) of the `X` column and `Fx` column. `Y`, `Z` and `Fy`, `Fz` columns are expected to be placed respectively after the `X` column and `Fx` one.
**More than one EM force file can be interpolated in the same run**.
- *Mechanical Mesh*: path to the .csv file describing the nodes of the mechanical mesh onto which forces have to be interpolated. The GUI allows to indicate the column index of the `node number` and the `X` coordinate (in meters). `Y` and `Z` coordinates columns are expected after the `X` one.
- *Output directory* folder where all outputs of the interpolation will be stored.

In addition to these paths, the interpolation parameters described in the [algorithm](#description-of-available-algorithms) section must be set.

### Interpolation Tab
The following is a description of the action buttons of the interpolation tab:

- *Run All*: equivalent to clicking all buttons in sequence except for *Preview Forces*.
- *Initialize interpolator*: builds the KDTree and pre-compute all the mech neighbours of each EM centroid.
- *Interpolate*: performs the interpolation of all EM force files provided.
- *Export Checks*: export a .csv containing forces and moments summaries of all interpolations.
- *Export ANSYS*: export one force file for each interpolation ready to be used with the `/INPUT` command of APDL. The file has the format `F, <node_ID>, Fx, <value>`.
- *Compute VTK*: build vtk objects for original and interpolated forces point clouds.
- *Export VTK*: export the vtk objects to .vtk files.
- *Preview Forces*: preview a comparison between original and interpolated EM forces to video in the GUI. Sliders are provided at the bottom of the pane to scale up or down the gliph arrows for better visibility purposes.

## Description of available algorithms

The interpolation algorithm is based on K-Dimensional Trees ([KDTree](https://en.wikipedia.org/wiki/K-d_tree)), a way to organize points in a K-dimensional space which grants fast querys.

### KDTree neighbours
There are different ways to search for "close" points into a KDTree (i.e. neighbours). The following are the type of queries that are currently implemented here:

* K-Nearest: select the K closest mech nodes to the EM node.
* Radius: select all mech nodes contained by a sphere of radius R centered on the EM node.

Two additional parameters are provided independently of the neighbour selection strategy:

* maximum distance cut-off: mech nodes farther than distance will be disregarded (more useful with k-nearest strategies).
* coincidence tolerance: distance at which a mech node and em node should be considered coincident.
In this case, no interpolation is called and the EM force is entirely assigned to the coincident mech node.

### Interpolation kernels
Once the neighbours are found, there may be different ways to distribute the original EM force on the selected mechanical nodes. The following are the currently available interpolation kernels:

* Weight by distance: distribute the forces invertionally proportional to the distance from the EM node.
* FEM based: connect each mech node with a stiff beam to the EM node and distribute forces in order to have the same resultant force and a moment equal to zero.

## Developer section

### Developer install

First git clone the GitHub repository to your local hardware.

Create a fresh python environment using:

```
conda create -n <env_name> python=<python_version>
```

activate the new environment and install the package in editable mode and with additional dev dependencies:

```
pip install -e .[dev]
```