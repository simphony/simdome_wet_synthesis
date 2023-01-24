"""Tests the SimPhoNy wrapper API methods."""

import unittest, os
from uuid import UUID

from common import generate_cuds, get_cuds
from osp.core.cuds import Cuds
from osp.core.namespaces import wet_synthesis

from osp.wrappers.wet_synthesis_wrappers import CompartmentSession
from osp.wrappers.wet_synthesis_wrappers.utils import plot_size_dist
from osp.core.utils import pretty_print


class TestWrapper(unittest.TestCase):
    """Test of all wrapper API methods for the CompartmentSession."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`. This function
        runs before each test method from this test case.
        """
        self.template_wrapper = generate_cuds()

    def test_str(self):
        """Tests the `__str__` method of the session."""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            try:
                self.assertIsInstance(str(session), str)
                self.assertIn('compartmental', str(session).lower())
            finally:
                session.close()

    def test_load_from_backend(self):
        """Tests the `_load_from_backend` method of the session."""
        with CompartmentSession(
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

        cuds = get_cuds(self.template_wrapper)
        accuracy = cuds['accuracy_level']
        press = cuds['pressure']
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
            wrapper.add(accuracy, press, temp, rotation, solid, metals, nh3, naoh, sizeDist, compartmentNet)

            session._apply_added(wrapper, 0)

            self.assertTrue(session._initialized)

    def test_initialize_and_run_and_close(self):
        """Runs the simulation.

        Running the simulation for the first time involves calling the
        `_initialize` method, the `_run` method and then the 'close' method.
        """
        cuds = get_cuds(self.template_wrapper)
        accuracy = cuds['accuracy_level']
        press = cuds['pressure']
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
            wrapper =  wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(accuracy, press, temp, rotation, solid, metals, nh3, naoh, sizeDist, compartmentNet)

            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])

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

            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])
            compartments = wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0]
            comp_i = compartments.get(oclass=wet_synthesis.Compartment)[-1]
            epsilon = comp_i.get(oclass=wet_synthesis.TurbulentDissipationRate)[0].value
            self.assertEqual(0.011057444226231, epsilon)

        self.assertFalse(os.path.isdir(simulation_dir))

if __name__ == '__main__':
    unittest.main()
