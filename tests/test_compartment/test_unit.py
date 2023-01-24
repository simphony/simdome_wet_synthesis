"""Unit test examples, both at the "system" level and the "method" level."""

import unittest, os, inspect, shutil

import matplotlib.pyplot as plt
import numpy as np
from osp.core.cuds import Cuds
from osp.core.namespaces import wet_synthesis

from common import generate_cuds, get_cuds
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
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            session._case_dir = os.path.join(currentDir, 'data')

            res = session._extract_moments()

            self.assertIsInstance(res, list)

    def test_update_size_dist_cud(self):
        """Test the _update_size_dist_cud method"""
        cuds = get_cuds(self.template_wrapper)
        sizeDist = cuds['sizeDistribution']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(sizeDist)

            session._case_dir = os.path.join(currentDir, 'data')

            session._update_size_dist_cud(wrapper)

            pretty_print(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])

            plot_size_dist(wrapper.get(oclass=wet_synthesis.SizeDistribution)[0])
            sizes = wrapper.get(oclass=wet_synthesis.SizeDistribution)[0]
            bin_i = sizes.get(oclass=wet_synthesis.Bin)[-1]
            diameter = bin_i.get(oclass=wet_synthesis.ParticleDiameter)[0].value
            self.assertEqual(14.937747721795278, diameter)

    def test_update_compartment_cuds(self):
        """Test the _select_mesh method"""
        cuds = get_cuds(self.template_wrapper)
        compartmentNet = cuds['compartmentNetwork']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(compartmentNet)

            session._case_dir = os.path.join(currentDir, 'data')
            session._update_compartment_cuds(wrapper)

            pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])
            compartments = wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0]
            comp_i = compartments.get(oclass=wet_synthesis.Compartment)[-1]
            epsilon = comp_i.get(oclass=wet_synthesis.TurbulentDissipationRate)[0].value
            self.assertEqual(0.014633708450457, epsilon)

    def test_select_mesh(self):
        """Test the _select_mesh method"""
        cuds = get_cuds(self.template_wrapper)
        accuracy = cuds['accuracy_level']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(accuracy)

            accuracy_level = wrapper.get(oclass=wet_synthesis.SliderAccuracyLevel)[0]

            res = session._select_mesh(accuracy_level)

            self.assertIsInstance(res, str)
            self.assertEqual('polyMesh_refinementLevel_0.zip', res)

    def test_insert_data(self):
        """Test the _insert_data method"""
        cuds = get_cuds(self.template_wrapper)
        temp = cuds['temperature']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(temp)

            dataDict = dict()

            name = 'temperature'

            res = session._insert_data('Temperature', wrapper, name, dataDict)

            self.assertIsInstance(res, float)
            self.assertEqual(298.15, res)
            self.assertIsInstance(dataDict, dict)
            self.assertEqual(298.15, dataDict[name])

    def test_insert_feed(self):
        """Test the _insert_feed method"""
        cuds = get_cuds(self.template_wrapper)
        metals = cuds['metals']
        nh3 = cuds['nh3']
        naoh = cuds['naoh']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(metals, nh3, naoh)

            dataDict = dict()

            feed = wrapper.get(oclass=wet_synthesis.Feed)[2]
            component = feed.get(oclass=wet_synthesis.Component)[0]
            name = 'flowrate_' + feed.name
            conc = 'conc_in_' + component.name
            
            session._insert_feed(feed, dataDict)

            self.assertIsInstance(dataDict, dict)
            self.assertEqual(1.226646, (dataDict[name]/session._conversionFactors["FlowRate"]))
            self.assertEqual(5, dataDict[conc])

    def test_mixed_conc(self):
        """Test the _mixed_conc method"""
        cuds = get_cuds(self.template_wrapper)
        metals = cuds['metals']
        nh3 = cuds['nh3']
        naoh = cuds['naoh']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(metals, nh3, naoh)

            feeds = wrapper.get(oclass=wet_synthesis.Feed)
    
            mix_conc = session._mixed_conc('nh3', 'nh3', feeds)

            self.assertIsInstance(mix_conc, float)
            self.assertEqual(1.0, round(mix_conc))

    def test_residence_time(self):
        """Test the _residence_time method"""
        cuds = get_cuds(self.template_wrapper)
        metals = cuds['metals']
        nh3 = cuds['nh3']
        naoh = cuds['naoh']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(metals, nh3, naoh)

            feeds = wrapper.get(oclass=wet_synthesis.Feed)
            reactor_volume = 0.00306639

            residence_time = session._residence_time(feeds, reactor_volume)

            self.assertIsInstance(residence_time, float)
            self.assertEqual(3600, round(residence_time))

    def test_estimate_end_time(self):
        """Test the _estimate_end_time method"""
        cuds = get_cuds(self.template_wrapper)
        metals = cuds['metals']
        nh3 = cuds['nh3']
        naoh = cuds['naoh']

        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)
            wrapper.add(metals, nh3, naoh)

            feeds = wrapper.get(oclass=wet_synthesis.Feed)
            reactor_volume = 0.00306639

            end_time = session._estimate_end_time(feeds, reactor_volume)

            self.assertIsInstance(end_time, int)
            self.assertEqual(18000, end_time)

    def test_estimate_time_intervals(self):
        """Test the _estimate_time_intervals method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=18060,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=False) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            times = session._estimate_time_intervals()

            self.assertIsInstance(times, object)
            self.assertEqual(14, np.size(times))
            self.assertEqual(6060, int(times[3]))

    def test_write_dict(self):
        """Test the _write_dict method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
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
            
            self.assertEqual('temperature 298.15;\n', l)

            shutil.rmtree(input_dir)

    def test_update_files(self):
        """Test the _update_files method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

            session._case_dir = os.path.join(currentDir, 'data')
            dataDict = dict({'temperature': 298.15,
                            'crystal_density': 3953,
                            'crystal_MW': 92.338,
                            'shape_factor': 0.523599,
                            'conc_in_nickel': 1.6,
                            'conc_in_manganese': 0.2,
                            'conc_in_cobalt': 0.2,
                            'conc_in_so4': 2.0,
                            'conc_in_nh3': 10.0,
                            'conc_in_na': 5.0})


            input_dir = os.path.join(currentDir, 'data', 'compartmentSimulation')
            shutil.copy(input_dir+'/caseSetup.yml', input_dir+'/caseSetup_bkp.yml')
            shutil.copy(input_dir+'/extract_info.py', input_dir+'/extract_info_bkp.py')
            shutil.copy(input_dir+'/react_division.py', input_dir+'/react_division_bkp.py')
            shutil.copy(input_dir+'/importScripts/NiMnCoHydroxidePrec.py', input_dir+'/importScripts/NiMnCoHydroxidePrec_bkp.py')
            shutil.copy(input_dir+'/importScripts/init_run.py', input_dir+'/importScripts/init_run_bkp.py')
            shutil.copy(input_dir+'/importScripts/read_files.py', input_dir+'/importScripts/read_files_bkp.py')

            session._update_files(dataDict)

            res_path = os.path.join(input_dir, "caseSetup.yml")
            f = open(res_path, 'r')
            lines = f.readlines()
            f.close()
            for i, line in enumerate(lines):
                if 'T:' in line:
                    self.assertIn('T: 298.15', line)
                if 'density:' in line:
                    self.assertIn('density: 3953', line)
                if 'numOfNodes:' in line:
                    self.assertIn('numOfNodes: 2', line)
                if 'metals:' in line:
                    self.assertIn('[1.6, 0.2, 0.2, 0, 0, 2.0]', lines[i+1])
                if 'nh3:' in line:
                    self.assertIn('[0, 0, 0, 10.0, 0, 0]', lines[i+1])
                if 'naoh:' in line:
                    self.assertIn('[0, 0, 0, 0, 5, 0]', lines[i+1])
            os.remove(res_path)
            os.rename(input_dir+'/caseSetup_bkp.yml', input_dir+'/caseSetup.yml')

            res_path = os.path.join(input_dir, 'importScripts', 'NiMnCoHydroxidePrec.py')
            f = open(res_path, 'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                if 'self.kv =' in line:
                    self.assertIn('self.kv = 0.523599', line)
            os.remove(res_path)
            os.rename(input_dir+'/importScripts/NiMnCoHydroxidePrec_bkp.py', input_dir+'/importScripts/NiMnCoHydroxidePrec.py')

            res_path = os.path.join(input_dir, 'importScripts', 'init_run.py')
            f = open(res_path, 'r')
            lines = f.readlines()
            f.close()
            for i, line in enumerate(lines):
                if 'cationConcRatios[i] * (atomicMass[i]' in line:
                    self.assertIn('aMassCrystal = 92.338', lines[i+1])
            os.remove(res_path)
            os.rename(input_dir+'/importScripts/init_run_bkp.py', input_dir+'/importScripts/init_run.py')

            name_list = ['/extract_info.py', '/react_division.py', '/importScripts/read_files.py']
            for name in name_list:
                f = open(input_dir+name, 'r')
                lines = f.readlines()
                f.close()
                for line in lines:
                    if 'time_dir =' in line:
                        self.assertIn("time_dir = '0.0011'", line)
                os.remove(input_dir+name)
            os.rename(input_dir+'/extract_info_bkp.py', input_dir+'/extract_info.py')
            os.rename(input_dir+'/react_division_bkp.py', input_dir+'/react_division.py')
            os.rename(input_dir+'/importScripts/read_files_bkp.py', input_dir+'/importScripts/read_files.py')

    def test_engine_specialization(self):
        """Test the _write_dict method"""
        with CompartmentSession(
                engine="pisoPrecNMC", case="precNMC",
                delete_simulation_files=False, end_time=0.0011,
                write_interval=1, num_moments=4,
                num_proc=1, dummy=True) as session:
            
            wet_synthesis.WetSynthesisWrapper(session=session)

            engine="pisoPrecNMC"
            session.engine_specialization(engine)

            self.assertEqual(1.0/3.6e6, session._conversionFactors["FlowRate"])

            
if __name__ == '__main__':
    unittest.main()
