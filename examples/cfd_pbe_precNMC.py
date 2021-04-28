# Example to use CFD-PBE wrapper
import traceback

from osp.wrappers.wet_synthesis_wrappers import CfdPbeSession
from osp.wrappers.wet_synthesis_wrappers.utils import plot_size_dist
from osp.core.namespaces import wet_synthesis
from osp.core.utils import pretty_print
from osp.core.utils import Cuds2dot


# create a wrapper session and run it
with CfdPbeSession(delete_simulation_files=False) as session:
    wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

    accuracy_level = wet_synthesis.SliderAccuracyLevel(number=6)
    wrapper.add(accuracy_level)

    pressure = wet_synthesis.Pressure(value=101325, unit='Pa')
    wrapper.add(pressure)

    temperature = wet_synthesis.Temperature(value=298.15, unit='K')
    wrapper.add(temperature)

    rotationalSpeed = wet_synthesis.RotationalSpeed(value=-1005, unit='rpm')
    wrapper.add(rotationalSpeed)

    density = wet_synthesis.Density(value=3953, unit='kg/m^3')
    molecularWeight = wet_synthesis.MolecularWeight(value=92.338, unit='g/mol')
    shapeFactor = wet_synthesis.ShapeFactor(value=0.523599, unit='')

    solidParticle = wet_synthesis.SolidParticle()
    solidParticle.add(density, rel=wet_synthesis.hasProperty)
    solidParticle.add(molecularWeight, rel=wet_synthesis.hasProperty)
    solidParticle.add(shapeFactor, rel=wet_synthesis.hasProperty)
    wrapper.add(solidParticle)

    ni_conc = wet_synthesis.MolarConcentration(value=1.14, unit='mol/lit')
    mn_conc = wet_synthesis.MolarConcentration(value=0.38, unit='mol/lit')
    co_conc = wet_synthesis.MolarConcentration(value=0.38, unit='mol/lit')
    nh3_conc = wet_synthesis.MolarConcentration(value=13.36, unit='mol/lit')
    naoh_conc = wet_synthesis.MolarConcentration(value=10, unit='mol/lit')

    ni = wet_synthesis.Component(name='nickel')
    mn = wet_synthesis.Component(name='manganese')
    co = wet_synthesis.Component(name='cobalt')
    nh3 = wet_synthesis.Component(name='nh3')
    naoh = wet_synthesis.Component(name='naoh')

    ni.add(ni_conc, rel=wet_synthesis.hasPart)
    mn.add(mn_conc, rel=wet_synthesis.hasPart)
    co.add(co_conc, rel=wet_synthesis.hasPart)
    nh3.add(nh3_conc, rel=wet_synthesis.hasPart)
    naoh.add(naoh_conc, rel=wet_synthesis.hasPart)

    metal_flowRate = wet_synthesis.FlowRate(value=2.1977, unit='lit/hr')
    nh3_flowRate = wet_synthesis.FlowRate(value=0.2184, unit='lit/hr')
    naoh_flowRate = wet_synthesis.FlowRate(value=0.9171, unit='lit/hr')

    metalFeed = wet_synthesis.Feed(name='metals')
    nh3Feed = wet_synthesis.Feed(name='nh3')
    naohFeed = wet_synthesis.Feed(name='naoh')

    metalFeed.add(ni, mn, co, rel=wet_synthesis.hasPart)
    metalFeed.add(metal_flowRate, rel=wet_synthesis.hasPart)

    nh3Feed.add(nh3, rel=wet_synthesis.hasPart)
    nh3Feed.add(nh3_flowRate, rel=wet_synthesis.hasPart)

    naohFeed.add(naoh, rel=wet_synthesis.hasPart)
    naohFeed.add(naoh_flowRate, rel=wet_synthesis.hasPart)

    wrapper.add(metalFeed)
    wrapper.add(nh3Feed)
    wrapper.add(naohFeed)

    Cuds2dot(wrapper).render()

    sizeDistribution = wet_synthesis.SizeDistribution()
    wrapper.add(sizeDistribution)

    pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

    try:
        # run the session
        session.run()

        pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

        plot_size_dist(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

    except Exception as e:
        print(e)
        traceback.print_exc()
        # session._delete_simulation_files = True
