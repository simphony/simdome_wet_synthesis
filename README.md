# Wet Synthesis

<!---introduction-start-c0e9f6f2-->

A collection of [SimPhoNy](https://github.com/simphony/simphony-osp)
[wrappers](https://simphony.readthedocs.io/en/v3.9.0/overview.html#fetch-data-from-a-database-run-a-simulation-and-immediately-store-the-results)
around a CFD-PBE solver to simulate the wet-synthesis of Ni-Mn-Co Hydroxides.

- CFD-PBE Wrapper: This wrapper prepares a simulation case folder based on the
  user inputs and executes a solver for Computational Fluid Dynamics-Population
  Balance Equation (CFD-PBE) simulation of NMC hydroxide precipitation. 

- Compartment Wrapper: This wrapper is aimed at simulating the NMC hydroxide 
  precipitation in a pilot CSTR reactor, by using the compartment model. 
  Currently, it can be used only to divide the reactor into the compartments.

*Contact*: [Andrea Querio](mailto:andrea.querio@polito.it), 
[Daniele Marchisio](mailto:daniele.marchisio@polito.it), 
[Antonio Buffo](mailto:antonio.buffo@polito.it) and 
[Gianluca Boccardo](mailto:gianluca.boccardo@polito.it) from the 
[Multiphase Systems and Chemical Engineering research group](https://www.disat.polito.it/research/research_groups/musychen), 
[Politecnico di Torino](https://www.polito.it/).

<!---introduction-end-c0e9f6f2-->

## Installation

<!---installation-start-880c326a-->

The wet synthesis wrappers require a working installation of 
[OpenFOAM 8](https://openfoam.org/version/8/), 
[SUNDIALS](https://github.com/LLNL/sundials) 
([v6.1.1](https://github.com/LLNL/sundials/releases/tag/v6.1.1) is known to 
work),
[7-zip](https://www.7-zip.org/),
[Anaconda3](https://www.anaconda.com/)
([v4.8.2](https://repo.anaconda.com/archive/) is known to work). Follow the links to find 
installation instructions for each tool.

In addition, to use the CFD-PBE Wrapper, it's necessary download the solver from the GitHub repository of Politecnico di Torino.

```shell
git clone https://github.com/mulmopro/wet-synthesis-route.git
```

After downloading it, enter the right directory and compile it.

NOTE: before start the compilation, make sure to put the correct path to the sundials libraries
in the *Allwmake* file in the *wet-synthesis-route/cfd_pbe_openfoam_solver/* directory.

```shell
cd wet-synthesis-route/cfd_pbe_openfoam_solver/
./Allwmake
cd ../cfd_onlyEnv/
./Allwmake
```

Instead, to use the Compartment Wrapper, install the following package.

```shell
conda install mkl-service
```

Once the requirements have been installed, clone the Wet Synthesis Wrappers 
repository and install them.

```shell
git clone https://github.com/simphony/simdome_wet_synthesis.git
pip install ./simdome_wet_synthesis
```

Then install the required ontology.

```shell
pico install simdome_wet_synthesis/ontology.wet_synthesis.yml

# If you have issues using pico directly, you can use
# python -m osp.core.pico install simdome_wet_synthesis/ontology.wet_synthesis.yml
```

<!---installation-end-880c326a-->

<!---installation-start-f7fde43d-->

### Docker 

Alternatively, it is possible to execute the wrapper in a Docker container.
Clone the repository and enter the newly created directory

```shell
git clone https://github.com/simphony/simdome_wet_synthesis.git
cd simdome_wet_synthesis
```

and then run

```sh
docker build -t simdome/wet_synthesis .
```

to create the docker image. After that, run

```sh
./run_container.sh
```

to get access to a shell inside a container based on the image that has just
been built.

<!---installation-end-f7fde43d-->

## Documentation

Visit [the documentation](https://simdomewetsynthesis.readthedocs.io)
to learn how to use the wrappers.