# Example to use CFD-PBE wrapper
import sys
import traceback
import argparse

from osp.wrappers.wet_synthesis_wrappers import CfdPbeSession
from osp.wrappers.wet_synthesis_wrappers.utils import plot_size_dist
from osp.core.namespaces import wet_synthesis
from osp.core.utils import pretty_print
from osp.core.utils import Cuds2dot

print('Hello')

def main(argv):

    parser = argparse.ArgumentParser(description='Process command-line inputs')

    parser.add_argument('--delete', action='store_true')
    parser.add_argument('--dummy', action='store_true')
    parser.add_argument('-n', '--numproc', type=int, default=1)
    parser.add_argument('-t', '--endtime', type=float, default=None)
    parser.add_argument('-w', '--writeinterval', type=int, default=None)

    args, _ = parser.parse_known_args(argv)

    # create a wrapper session and run it
    with CfdPbeSession(
            engine="pisoPrecNMC", case="precNMC",
            delete_simulation_files=args.delete, end_time=args.endtime,
            write_interval=args.writeinterval, num_moments=4,
            num_proc=args.numproc, dummy=args.dummy) as session:

        wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

        accuracy_level = wet_synthesis.SliderAccuracyLevel(number=0)
        wrapper.add(accuracy_level)

        pressure = wet_synthesis.Pressure(value=101325, unit='Pa')
        wrapper.add(pressure)

        temperature = wet_synthesis.Temperature(value=298.15, unit='K')
        wrapper.add(temperature)

        rotationalSpeed = wet_synthesis.RotationalSpeed(value=200, unit='rpm')
        wrapper.add(rotationalSpeed)

        density = wet_synthesis.Density(value=3953, unit='kg/m^3')
        molecularWeight = wet_synthesis.MolecularWeight(
            value=92.338, unit='g/mol')
        shapeFactor = wet_synthesis.ShapeFactor(value=0.523599, unit='')

        solidParticle = wet_synthesis.SolidParticle()
        solidParticle.add(density, rel=wet_synthesis.hasProperty)
        solidParticle.add(molecularWeight, rel=wet_synthesis.hasProperty)
        solidParticle.add(shapeFactor, rel=wet_synthesis.hasProperty)
        wrapper.add(solidParticle)

        ni_conc = wet_synthesis.MolarConcentration(value=1.6, unit='mol/lit')
        mn_conc = wet_synthesis.MolarConcentration(value=0.2, unit='mol/lit')
        co_conc = wet_synthesis.MolarConcentration(value=0.2, unit='mol/lit')
        so4_conc = wet_synthesis.MolarConcentration(value=2.0, unit='mol/lit')
        nh3_conc = wet_synthesis.MolarConcentration(value=10, unit='mol/lit')
        na_conc = wet_synthesis.MolarConcentration(value=5, unit='mol/lit')

        ni = wet_synthesis.Component(name='nickel')
        mn = wet_synthesis.Component(name='manganese')
        co = wet_synthesis.Component(name='cobalt')
        so4 = wet_synthesis.Component(name='so4')
        nh3 = wet_synthesis.Component(name='nh3')
        na = wet_synthesis.Component(name='na')

        ni.add(ni_conc, rel=wet_synthesis.hasPart)
        mn.add(mn_conc, rel=wet_synthesis.hasPart)
        co.add(co_conc, rel=wet_synthesis.hasPart)
        so4.add(so4_conc, rel=wet_synthesis.hasPart)
        nh3.add(nh3_conc, rel=wet_synthesis.hasPart)
        na.add(na_conc, rel=wet_synthesis.hasPart)

        metal_flowRate = wet_synthesis.FlowRate(value=1.5330924, unit='lit/hr')
        nh3_flowRate = wet_synthesis.FlowRate(value=0.30666132, unit='lit/hr')
        naoh_flowRate = wet_synthesis.FlowRate(value=1.226646, unit='lit/hr')

        metalFeed = wet_synthesis.Feed(name='metals')
        nh3Feed = wet_synthesis.Feed(name='nh3')
        naohFeed = wet_synthesis.Feed(name='naoh')

        metalFeed.add(ni, mn, co, so4, rel=wet_synthesis.hasPart)
        metalFeed.add(metal_flowRate, rel=wet_synthesis.hasPart)

        nh3Feed.add(nh3, rel=wet_synthesis.hasPart)
        nh3Feed.add(nh3_flowRate, rel=wet_synthesis.hasPart)

        naohFeed.add(na, rel=wet_synthesis.hasPart)
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


if __name__ == "__main__":

    main(sys.argv[1:])
