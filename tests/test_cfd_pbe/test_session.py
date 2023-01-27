"""Tests the SimPhoNy wrapper API methods."""

import unittest, os, inspect
from uuid import UUID

from common import generate_cuds, get_cuds
from osp.core.cuds import Cuds
from osp.core.namespaces import wet_synthesis

from osp.wrappers.wet_synthesis_wrappers import CfdPbeSession
from osp.wrappers.wet_synthesis_wrappers.utils import plot_size_dist
from osp.core.utils import pretty_print

frame = inspect.currentframe()
filePath = inspect.getfile(frame)
currentDir = os.path.realpath(os.path.abspath(os.path.dirname(filePath)))


class TestWrapper(unittest.TestCase):
    """Test of all wrapper API methods for the CfdPbeSession."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`. This function
        runs before each test method from this test case.
        """
        self.template_wrapper = generate_cuds()

    def test_str(self):
        """Tests the `__str__` method of the session."""
        with CfdPbeSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:

            self.assertIsInstance(str(session), str)
            self.assertIn('cfd-pbe', str(session).lower())

    def test_load_from_backend(self):
        """Tests the `_load_from_backend` method of the session."""
        with CfdPbeSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            temp = wet_synthesis.Temperature(value=298.15, unit='K')

            fake_uid = UUID(int=8)

            self.assertListEqual(
                [None],
                list(session._load_from_backend([fake_uid])))
            self.assertListEqual(
                [temp.uid],
                list(x.uid
                    for x in session._load_from_backend([temp.uid])))

    def test_apply_addedd(self):
        """Tests the `_apply_added` method of the session."""

        with CfdPbeSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(*self.template_wrapper.get())

            session._apply_added(wrapper, 0)

            self.assertTrue(session._initialized)

    def test_initialize_and_run_and_close(self):
        """Runs the simulation.

        Running the simulation for the first time involves calling the
        `_initialize` method, the `_run` method and then the 'close' method.
        """
        with CfdPbeSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            wrapper =  wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(*self.template_wrapper.get())

            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

            # Run the session
            session.run()

            simulation_dir = session._case_dir

            self.assertTrue(session._initialized)

            # Get the results
            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            plot_size_dist(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            sizes = wrapper.get(oclass=wet_synthesis.SizeDistribution)[0]
            bin_i = sizes.get(oclass=wet_synthesis.Bin)[-1]
            diameter = bin_i.get(oclass=wet_synthesis.ParticleDiameter)[0].value
            self.assertEqual(14.937747721795278, diameter)

        self.assertFalse(os.path.isdir(simulation_dir))

if __name__ == '__main__':
    unittest.main()
