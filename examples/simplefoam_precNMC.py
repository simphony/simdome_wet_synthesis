# Example to use PrecFOAM wrapper
import traceback

from osp.wrappers.prec_nmc_wrappers import PrecFoamSession
from osp.wrappers.prec_nmc_wrappers.utils import plot_size_dist
from osp.core.namespaces import prec_nmc
from osp.core.utils import pretty_print
from osp.core.utils import Cuds2dot


# create a wrapper session and run it
with PrecFoamSession(delete_simulation_files=False) as session:
    wrapper = prec_nmc.PrecNMCWrapper(session=session)

    accuracy_level = prec_nmc.SliderAccuracyLevel(number=6)
    wrapper.add(accuracy_level)

    pressure = prec_nmc.Pressure(value=101325, unit='Pa')
    wrapper.add(pressure)

    temperature = prec_nmc.Temperature(value=298.15, unit='K')
    wrapper.add(temperature)

    rotationalSpeed = prec_nmc.RotationalSpeed(value=-1005, unit='rpm')
    wrapper.add(rotationalSpeed)

    density = prec_nmc.Density(value=3953, unit='kg/m^3')
    molecularWeight = prec_nmc.MolecularWeight(value=92.3383, unit='g/mol')
    shapeFactor = prec_nmc.ShapeFactor(value=0.523599, unit='')

    solidParticle = prec_nmc.SolidParticle()
    solidParticle.add(density, rel=prec_nmc.hasProperty)
    solidParticle.add(molecularWeight, rel=prec_nmc.hasProperty)
    solidParticle.add(shapeFactor, rel=prec_nmc.hasProperty)
    wrapper.add(solidParticle)

    ni_conc = prec_nmc.MolarConcentration(value=1.14, unit='mol/lit')
    mn_conc = prec_nmc.MolarConcentration(value=0.38, unit='mol/lit')
    co_conc = prec_nmc.MolarConcentration(value=0.38, unit='mol/lit')
    nh3_conc = prec_nmc.MolarConcentration(value=13.36, unit='mol/lit')
    naoh_conc = prec_nmc.MolarConcentration(value=10, unit='mol/lit')

    ni = prec_nmc.Component(name='nickel')
    mn = prec_nmc.Component(name='manganese')
    co = prec_nmc.Component(name='cobalt')
    nh3 = prec_nmc.Component(name='nh3')
    naoh = prec_nmc.Component(name='naoh')

    ni.add(ni_conc, rel=prec_nmc.hasPart)
    mn.add(mn_conc, rel=prec_nmc.hasPart)
    co.add(co_conc, rel=prec_nmc.hasPart)
    nh3.add(nh3_conc, rel=prec_nmc.hasPart)
    naoh.add(naoh_conc, rel=prec_nmc.hasPart)

    metal_flowRate = prec_nmc.FlowRate(value=2.1977, unit='lit/hr')
    nh3_flowRate = prec_nmc.FlowRate(value=0.2184, unit='lit/hr')
    naoh_flowRate = prec_nmc.FlowRate(value=0.9171, unit='lit/hr')

    metalFeed = prec_nmc.Feed(name='metals')
    nh3Feed = prec_nmc.Feed(name='nh3')
    naohFeed = prec_nmc.Feed(name='naoh')

    metalFeed.add(ni, mn, co, rel=prec_nmc.hasPart)
    metalFeed.add(metal_flowRate, rel=prec_nmc.hasPart)

    nh3Feed.add(nh3, rel=prec_nmc.hasPart)
    nh3Feed.add(nh3_flowRate, rel=prec_nmc.hasPart)

    naohFeed.add(naoh, rel=prec_nmc.hasPart)
    naohFeed.add(naoh_flowRate, rel=prec_nmc.hasPart)

    wrapper.add(metalFeed)
    wrapper.add(nh3Feed)
    wrapper.add(naohFeed)

    Cuds2dot(wrapper).render()

    sizeDistribution = prec_nmc.SizeDistribution()
    wrapper.add(sizeDistribution)

    pretty_print(wrapper.get(oclass=prec_nmc.SizeDistribution)[0])

    try:
        # run the session
        session.run()

        pretty_print(wrapper.get(oclass=prec_nmc.SizeDistribution)[0])

        plot_size_dist(wrapper.get(oclass=prec_nmc.SizeDistribution)[0])

    except Exception as e:
        print(e)
        traceback.print_exc()
        # session._delete_simulation_files = True
