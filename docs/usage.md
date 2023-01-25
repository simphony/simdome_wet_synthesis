# Usage

The SimDOME Wet Synthesis Wrappers can be applied to two use-cases.

- CFD-PBE Wrapper
- Compartment Wrapper

A brief description of each use case can be found on the 
[introductory page](index.md).

The simulation inputs must be instantiated as 
[CUDS objects](https://simphony.readthedocs.io/en/v3.9.0/jupyter/cuds_api.html)
using the entities from the `wet_synthesis` namespace. The namespace is 
included in the Wet Synthesis ontology (see 
[installation](installation.md)). The instantiation can be done directly in the
corresponding wrapper session, by spawning either a 
`osp.wrappers.wet_synthesis_wrappers.CfdPbeSession` object for the CFD-PBE 
Wrapper use-case or a `osp.wrappers.wet_synthesis_wrappers.CompartmentSession`
for the Compartment Wrapper use-case. To access the `wet_synthesis` namespace 
and the two session classes, you may import them as follows.

```python
from osp.core.namespaces import wet_synthesis
from osp.wrappers.wet_synthesis_wrappers import CfdPbeSession
from osp.wrappers.wet_synthesis_wrappers import CompartmentSession
```

A diagram depicting the input and output patterns of CUDS objects that the 
wrappers expect and produce is shown below.

<figure style="display: table; text-align:center; margin-left: auto; margin-right:auto">

![Wet Synthesis inputs and outputs](./static/graph_pattern.drawio.svg)

<figcaption style="display: table-caption; caption-side: bottom; text-align:center">

_Diagram showing the pattern of input CUDS objects that the Wet Synthesis 
Wrappers expect to find in the session's knowledge graph and the CUDS objects 
that are produced as simulation outputs._

</figcaption>
    
</figure>

Once you have imported the namespace and the session class of your choice, you 
may instantiate your inputs, run the simulation, and process the results.

```python
with CfdPbeSession(end_time=None, write_interval=None,
                   num_moments=4, num_proc=1,
                   dummy=False) as session:
    # Initialize the session with a `WetSynthesisWrapper` object.
    wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
    
    # Create and link your CUDS objects here.
    # accuracy_level = ..., pressure = ..., temperature = ...
    # ...
    # solid_particle.add(density, molecular_weight, shape_factor,
    #                    rel=wet_synthesis.hasProperty)
    # ...
    # wrapper.add(accuracy_level, pressure, size_distribution, ...)
    # ...
    
    # Run the simulation
    session.run()

    # Process and/or export your simulation results
    # ...
```

Both session classes accept several keyword arguments that control the 
simulation in various ways:

- `delete_simulation_files` _(default: `True`)_: As described in the 
  [installation section](installation.md), a "case folder" for OpenFOAM is 
  created from a template before the simulation is run. The folder is 
  additionally populated with results produced by OpenFOAM during the
  simulation. Some results are transformed into CUDS objects, but others are
  not. You can peek into this folder to get this extra information, or 
  alternatively, set this keyword argument to `True` if you do not need it, so
  that the folder is automatically deleted when the simulation ends.
- `end_time`: Amount of simulated time to run OpenFOAM for (e.g. `0.03`). If 
  set to `None`, an automatic guess will be used instead.
- `write_interval`: Controls how often data is written to the OpenFOAM output
  file. If set to `None`, a default of `100` time steps is used.
- `num_moments`: A value needs to be set, but it will be ignored and replaced
  by `4`, since at the moment, the wrapper is not capable of adapting the case 
  template to more/fewer moments.
- `num_proc`: Number of processors to be used for the calculation (e.g. `3`).
- `dummy`: When set to `True`, a special dummy set of moments is used so that
  the simulation ends after a short time, useful for development and debugging 
  purposes. It should normally be set to `False`.

Two complete examples of use (one for each use case) are provided in the 
[`examples` folder](https://github.com/simphony/simdome_wet_synthesis/tree/master/examples).
