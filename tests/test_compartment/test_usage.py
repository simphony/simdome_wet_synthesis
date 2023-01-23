"""Test typical usage of the software (end-to-end test)."""

import unittest
import sys, traceback, argparse

from osp.core.namespaces import wet_synthesis
from osp.core.cuds import Cuds

from common import generate_cuds
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

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True) as session:

            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            session._dummy = True

            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])

            # Run the session
            session.run()

            simulation_dir = session._case_dir

            self.assertTrue(session._initialized)

            # Get the results
            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            plot_size_dist(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])


if __name__ == '__main__':
    unittest.main()