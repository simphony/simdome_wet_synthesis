# Wet Synthesis
A collection of wrappers around solvers that simulate the wet-synthesis of Ni-Mn-Co Hydroxides 

*Contact*: [Mohsen Shiea](mailto:mohsen.shiea@polito.it), 
[Daniele Marchisio](mailto:daniele.marchisio@polito.it), 
[Antonio Buffo](mailto:antonio.buffo@polito.it) and 
[Gianluca Boccardo](mailto:gianluca.boccardo@polito.it) from the 
Multiphase Systems and Chemical Engineering research group, Politecnico di Torino.

**Index**
- [Wet Synthesis](#Wet-Synthesis)
  - [CFD-PBE Wrapper](#CFD-PBE-Wrapper)
  - [Compartment Wrapper](#Compartment-Wrapper)
  - [Compatibility](#Compatibility)
  - [Requirements](#Requirements)
  - [Installation](#Installation)
  - [Docker Container](#Docker-Container)
  - [Usage](#Usage)

## CFD-PBE Wrapper
This wrapper prepares a simulation case folder based on the user inputs and executes a solver for Computational Fluid Dynamics-Population Balance Equation (CFD-PBE) simulation of NMC hydroxide precipitation. 
## Compartment Wrapper
This wrapper is aimed at simulating the NMC hydroxide precipitation in a pilot CSTR reactor, by using the compartment model. Currently, it can be used only to divide the reactor into the compartments.

## Requirements
- [OSP core](https://github.com/simphony/osp-core)
- [OpenFOAM](https://openfoam.org/)
- [Ansys Fluent](https://www.ansys.com/products/fluids/ansys-fluent)
- [7-zip](https://www.7-zip.org/)

## Compatibility

The following table describes the version compatibility between the [OSP core](https://github.com/simphony/osp-core) package and documentation presented in this project.

| __Wrapper development__ | __OSP core__ |
|:-----------------------:|:------------:|
|          1.0.0          |     3.4.x    |

The releases of OSP core are available [here](https://github.com/simphony/osp-core).

## Installation
### ontology:
```sh
pico install ontology.wet_synthesis.yml

# If you have issues using pico directly, you can use
python -m osp.core.pico install ontology.wet_synthesis.yml
```
### wrappers:
```sh
python3 setup.py install
```
More information can be found in the documentation for [installation of OSP core](https://simphony.readthedocs.io/en/latest/installation.html)

## Docker Container
### Image creation:
```sh
./docker_install.sh
```
### Launch container:
```sh
./run_container.sh
```

## Usage
Two scripts are provided in the folder "examples" for the usage of the wrappers. It should be noted that the user is responsible for providing the OpenFOAM solver or Ansys Fluent executables. Moreover, the user should place the template case folders and mesh files in the corresponding folders found in the address "osp/wrappers/wet_synthesis_wrappers/cases/precNMC".
