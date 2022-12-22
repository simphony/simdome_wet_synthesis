# Installation

```{include} ../README.md
   :start-after: <!---installation-start-880c326a-->
   :end-before: <!---installation-end-880c326a-->
```

```{note}
OpenFOAM uses a collection of files packed together in a so-called 
"case folder" as input. The Wet Synthesis Wrappers include templates for those 
case folders, that are modified before running each simulation according to the
parameters passed from SimPhoNy in the form of
[CUDS objects](https://simphony.readthedocs.io/en/v3.9.0/jupyter/cuds_api.html)
(see the [usage section](./usage.md)).

Such templates are included in the Python package, in the folder
`osp/wrappers/wet_synthesis_wrappers/cases`. If you wish OpenFOAM to behave
in a way that is not covered by the parameters that are passed from SimPhoNy,
then you will have to modify the case folder templates before installing the 
package.
```

```{include} ../README.md
   :start-after: <!---installation-start-f7fde43d-->
   :end-before: <!---installation-end-f7fde43d-->
```
