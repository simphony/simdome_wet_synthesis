"""Test typical usage of the software (end-to-end test)."""

import unittest
import sys, traceback, argparse

from osp.core.namespaces import wet_synthesis
from osp.core.cuds import Cuds

from tests.test_cfd_pbe.common import generate_cuds
from osp.wrappers.wet_synthesis_wrappers import CfdPbeSession
from osp.wrappers.wet_synthesis_wrappers.utils import plot_size_dist
from osp.core.utils import pretty_print


class TestWrapper(unittest.TestCase):
    """Typical usage of the CfdPbeSession."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`. This function
        runs before each test method from this test case.
        """
        self.template_wrapper = generate_cuds()

    def test_cfd_pbe(self):
        """SimDOME session for cfd-pbe simulation"""

        with CfdPbeSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True) as session:

            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            session._dummy = True

            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

            # Run the session
            session.run()
            self.assertTrue(session._initialized)

            # Get the results
            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

            plot_size_dist(
                wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])


if __name__ == '__main__':
    unittest.main()