"""Unit test examples, both at the "system" level and the "method" level."""

import unittest, os, inspect, shutil

import matplotlib.pyplot as plt
import numpy as np
from osp.core.cuds import Cuds
from osp.core.namespaces import wet_synthesis

from common import generate_cuds
from osp.wrappers.wet_synthesis_wrappers import CompartmentSession
from osp.wrappers.wet_synthesis_wrappers.utils import plot_size_dist
from osp.core.utils import pretty_print

frame = inspect.currentframe()
filePath = inspect.getfile(frame)
currentDir = os.path.realpath(os.path.abspath(os.path.dirname(filePath)))

class TestCompartmentSession(unittest.TestCase):
    """Tests the CompartmentSession.

    Tests at the method level the methods that do not belong to the wrapper
    API, such methods have been already tested in `test_session.py`.
    """
    session: CompartmentSession
    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.template_wrapper = generate_cuds()

    def test_extract_moments(self):
        """Test the _extract_moments method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            session._case_dir = os.path.join(currentDir, 'data')

            res = session._extract_moments()

            self.assertIsInstance(res, list)

    def test_update_size_dist_cud(self):
        """Test the _update_size_dist_cud method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            session._case_dir = os.path.join(currentDir, 'data')

            session._update_size_dist_cud()

            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

            plot_size_dist(
                wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

    def test_update_compartment_cuds(self):
        """Test the _select_mesh method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            session._case_dir = os.path.join(currentDir, 'data')
            session._update_compartment_cuds(wrapper)

            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])

    def test_select_mesh(self):
        """Test the _select_mesh method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            accuracy_level = wrapper.get(oclass=wet_synthesis.SliderAccuracyLevel)[0]

            res = session._select_mesh(accuracy_level)

            self.assertIsInstance(res, str)
            self.assertEqual('polyMesh_refinementLevel_0.zip', res)

    def test_insert_data(self):
        """Test the _insert_data method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            dataDict = dict()

            name = 'temperature'

            res = session._insert_data('Temperature', wrapper, name, dataDict)

            self.assertIsInstance(res, float)
            self.assertEqual(298.15, res)
            self.assertIsInstance(dataDict, dict)
            self.assertEqual(298.15, dataDict[name])

    def test_insert_feed(self):
        """Test the _insert_feed method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            dataDict = dict()

            feed = wrapper.get(oclass=wet_synthesis.Feed)[2]
            name = 'flowrate_' + feed.name
            conc = 'conc_in_' + feed.get(oclass=wet_synthesis.Component)[0]
            
            session._insert_feed(feed, dataDict)

            self.assertIsInstance(dataDict, dict)
            self.assertEqual(1.226646, dataDict[name])
            self.assertEqual(5, dataDict[conc])

    def test_mixed_conc(self):
        """Test the _mixed_conc method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            feeds = wrapper.get(oclass=wet_synthesis.Feed)
    
            mix_conc = session._mixed_conc('nh3', 'nh3', feeds)

            self.assertIsInstance(mix_conc, float)
            self.assertEqual(1.0, mix_conc)

    def test_residence_time(self):
        """Test the _residence_time method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            feeds = wrapper.get(oclass=wet_synthesis.Feed)
            reactor_volume = 0.00306639

            residence_time = session._residence_time(feeds, reactor_volume)

            self.assertIsInstance(residence_time, float)
            self.assertEqual(3600, round(residence_time))

    def test_estimate_end_time(self):
        """Test the _estimate_end_time method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            feeds = wrapper.get(oclass=wet_synthesis.Feed)
            reactor_volume = 0.00306639

            end_time = session._estimate_end_time(feeds, reactor_volume)

            self.assertIsInstance(end_time, int)
            self.assertEqual(18060, end_time)

    def test_estimate_time_intervals(self):
        """Test the _estimate_time_intervals method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=18060,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            times = session._estimate_time_intervals()

            self.assertIsInstance(times, object)
            self.assertEqual(14, np.size(times))
            self.assertEqual(6060, int(times[3]))

    def test_write_dict(self):
        """Test the _write_dict method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            session._case_dir = os.path.join(currentDir, 'data')
            dataDict = dict({'temperature': 298.15})
            input_dir = os.path.join(session._case_dir, 'include')
            os.makedirs(input_dir, exist_ok=True)

            session._write_dict(dataDict, "input", "include", "include_original")

            res_path = os.path.join(input_dir, "input")
            f = open(res_path, 'r')
            lines = f.readlines()
            f.close()

            for line in lines:
                if (line.find("temperature")>(-1)):
                    l = line
            
            self.assertEqual('temperature 298.15;', l)

            shutil.rmtree(input_dir)

    def test_update_files(self):
        """Test the _update_files method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            session._case_dir = os.path.join(currentDir, 'data')
            solidParticle = wrapper.get(oclass=wet_synthesis.SolidParticle)[0]

            session._update_files("/compartmentSimulation/caseSetup.yml", solidParticle, wrapper)

            input_dir = os.path.join(currentDir, 'data', 'compartmentSimulation')
            res_path = os.path.join(input_dir, "caseSetup.yml")
            f = open(res_path, 'r')
            lines = f.readlines()
            f.close()

            for line in lines:
                if (line.find("T:")>(-1)):
                    l = line
            
            self.assertEqual('T: 298.15', l)

    # def test_add_division(self):
    #     """Test the _write_dict method"""
    #     with CompartmentSession(
    #             engine="pisoPrecNMC", case="precNMC",
    #             delete_simulation_files=True) as session:
            
    #         wet_synthesis.WetSynthesisWrapper(session=session)

    def test_engine_specialization(self):
        """Test the _write_dict method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=True, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            engine = "pisoPrecNMC"

            session.engine_specialization(engine)

            self.assertEqual(1.0/3.6e6, self._conversionfactors["FlowRate"])

            
if __name__ == '__main__':
    unittest.main()
