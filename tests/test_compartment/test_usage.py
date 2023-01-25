"""Test typical usage of the software (end-to-end test)."""

import unittest
import sys, traceback, argparse

from osp.core.namespaces import wet_synthesis
from osp.core.cuds import Cuds

from common import generate_cuds, get_cuds
from osp.wrappers.wet_synthesis_wrappers import CompartmentSession
from osp.wrappers.wet_synthesis_wrappers.utils import plot_size_dist
from osp.core.utils import pretty_print


class TestWrapper(unittest.TestCase):
    """Typical usage of the CompartmentSession."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`. This function
        runs before each test method from this test case.
        """
        self.template_wrapper = generate_cuds()

    def test_compartment_model(self):
        """SimDOME session for cfd-pbe simulation"""

        cuds = get_cuds(self.template_wrapper)
        accuracy = cuds['accuracy_level']
        press = cuds['pressure']
        liquid_density = cuds['liquid_density']
        temp = cuds['temperature']
        rotation = cuds['rotationalSpeed']
        solid = cuds['solidParticle']
        metals = cuds['metals']
        nh3 = cuds['nh3']
        naoh = cuds['naoh']
        sizeDist = cuds['sizeDistribution']
        compartmentNet = cuds['compartmentNetwork']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:

            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(accuracy, press, liquid_density, temp, rotation, solid, metals, nh3, naoh, sizeDist, compartmentNet)

            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])

            # Run the session
            session.run()
            self.assertTrue(session._initialized)

            # Get the results
            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            plot_size_dist(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            sizes = wrapper.get(oclass=wet_synthesis.SizeDistribution)[0]
            bin_i = sizes.get(oclass=wet_synthesis.Bin)[-1]
            diameter = bin_i.get(oclass=wet_synthesis.ParticleDiameter)[0].value
            self.assertEqual(14.937747721795278, diameter)

            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])
            compartments = wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0]
            comp_i = compartments.get(oclass=wet_synthesis.Compartment)[-1]
            epsilon = comp_i.get(oclass=wet_synthesis.TurbulentDissipationRate)[0].value
            self.assertEqual(0.011057444226231, epsilon)


if __name__ == '__main__':
    unittest.main()