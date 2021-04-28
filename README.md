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

## CFD-PBE Wrapper
This wrapper prepares a simulation case folder based on the user inputs and executes a solver for Computational Fluid Dynamics-Population Balance Equation (CFD-PBE) simulation of NMC hydroxide precipitation. Currently, there is only one CFD-PBE solver available, which is developed by using the OpenFOAM software. 
## Compartment Wrapper
This wrapper is aimed at simulating the NMC hydroxide precipitation in a pilot CSTR reactor, by using the compartment model. Currently, it can be used only to divide the reactor into the compartments.  
## Compatibility

The following table describes the version compatibility between the [OSP core](https://github.com/simphony/osp-core) package and documentation presented in this project.

| __Wrapper development__ | __OSP core__ |
|:-----------------------:|:------------:|
|          1.0.0          |       3.4.x  |

The releases of OSP core are available [here](https://github.com/simphony/osp-core).

