import os
import subprocess
import shutil
import math
import numpy as np
import yaml

from osp.core.session import SimWrapperSession
from osp.core.namespaces import wet_synthesis
from osp.wrappers.wet_synthesis_wrappers.utils import reconstruct_log_norm_dist
from osp.wrappers.wet_synthesis_wrappers.utils import replace_char_in_keys
from osp.wrappers.wet_synthesis_wrappers.utils import read_compartment_data
from osp.wrappers.wet_synthesis_wrappers.utils import find_compartment_by_id


class CompartmentSession(SimWrapperSession):
    """
    Session class for compartment model
    """

    def __init__(self, engine="pisoPrecNMC", case="precNMC",
                 delete_simulation_files=True, **kwargs):

        # Set engine defaults
        self._end_time = kwargs.pop('end_time')
        self._write_interval = kwargs.pop('write_interval')

        self._num_moments = kwargs.pop('num_moments')
        # At the moment, the wrapper is not capable of adapting
        # the case template to more/less moments
        self._num_moments = 4

        self._num_proc = kwargs.pop('num_proc')

        self._dummy = kwargs.pop('dummy')

        super().__init__(engine, **kwargs)

        # Whether or not to store the generated files by the simulation engine
        self._delete_simulation_files = delete_simulation_files

        # Engine specific initializations
        self._initialized = False

        self._case_source = os.path.join(
            os.path.dirname(__file__), "cases", case)

        self._case_template = None
        self._exec = None
        self._mesh_info = None
        self._input_format = None
        self._conversionFactors = None
        self.engine_specialization(engine)

        self._case_dir = None

    def __str__(self):
        return "A session for NMC hydroxide precipitation compartmental solver"

    def close(self):
        """ Invoked, when the session is being closed """
        if self._delete_simulation_files and self._case_dir:
            shutil.rmtree(self._case_dir)
        # Reset the status of the class
        if self._initialized:
            self._initialized = False

    # OVERRIDE
    def _run(self, root_cuds_object):
        """ Runs the engine """
        if self._initialized:
            print("\n{} started\n".format(self._engine))
            cwd = self._case_dir + '/cfdSimulation/'
            retcode = subprocess.call(self._exec, cwd=cwd)

            if retcode == 0:
                print("\n{} CFD simulation finished successfully\n".format(self._engine))

            else:
                print("\n{} CFD simulation terminated with exit code {:d}\n".format(
                    self._engine, retcode))


            cwd = self._case_dir + '/compartmentSimulation/'
            retcode = subprocess.call(["./reactDivision"], cwd=cwd)

            if retcode == 0:
                print("\nReactor division finished successfully\n")

                self._update_compartment_cuds(root_cuds_object)
                print("Compartment data is updated\n")

            else:
                print("\nReactor division terminated with exit code {:d}\n".format(retcode))


            retcode = subprocess.call(["mpirun", "-np", str(self._num_proc), "python3", "runPrecSolver.py"], cwd=cwd)

            if retcode == 0:
                print("\nCompartment simulation finished successfully\n")

                self._update_size_dist_cud(root_cuds_object)

            else:
                print("\nCompartment simulation terminated with exit code {:d}\n".format(retcode))



    # OVERRIDE
    def _load_from_backend(self, uids, expired=None):
        """ Loads the cuds object from the simulation engine """
        for uid in uids:
            try:
                cuds_object = self._registry.get(uid)
            except KeyError:
                yield None

            yield cuds_object

    # OVERRIDE
    def _apply_added(self, root_obj, buffer):
        """ Adds the new cuds to the engine """
        if not self._initialized:
            self._initialize(root_obj, buffer)

    # OVERRIDE
    def _apply_updated(self, root_obj, buffer):
        """ Updates the changed cuds in the engine """
        pass

    # OVERRIDE
    def _apply_deleted(self, root_obj, buffer):
        """ Removes the deleted cuds from the engine """
        pass

    # OVERRIDE
    def _initialize(self, root_cuds_object, buffer):
        """ Set the solver dictionary files """

        # Copy the template folder
        self._case_dir = os.path.join(
            os.getcwd(),
            "simulation-wetSynthCompartment-%s" % root_cuds_object.uid)
        shutil.copytree(self._case_template, self._case_dir)

        input_dir = os.path.join(self._case_dir, 'cfdSimulation/include')
        os.makedirs(input_dir, exist_ok=True)

        # Extract data from CUDS
        accuracy_level = root_cuds_object.get(
            oclass=wet_synthesis.SliderAccuracyLevel)[0]

        # Select the mesh based on the accuracy level
        meshFileName = self._select_mesh(accuracy_level)

        meshSourcePath = os.path.join(
            self._case_source, "meshFiles", meshFileName)

        meshTargerPath = os.path.join(
            self._case_dir+'/cfdSimulation', "{:s}.{:s}".format(self._mesh_info["name"],
                                               self._mesh_info["ext"]))

        # Copy the mesh file
        if os.path.isfile(meshSourcePath):
            shutil.copy(meshSourcePath, meshTargerPath)
        else:
            raise Exception("Mesh file is missing")

        # Dictionary to insert the inputs
        dataDict = dict()

        # add the material
        # material = root_cuds_object.get(oclass=wet_synthesis.Material)[0]

        # Insert pressure into the input dictionary
        self._insert_data(
            'Pressure', root_cuds_object, 'outlet_pressure', dataDict)

        # Insert temperature into the input dictionary
        self._insert_data(
            'Temperature', root_cuds_object, 'temperature', dataDict)

        # Insert rotational speed into the input dictionary
        self._insert_data(
            'RotationalSpeed', root_cuds_object, 'angular_velocity', dataDict,
            conversionFactor=self._conversionFactors["RotationalSpeed"])

        # Add the particle properties to the input dictionary
        solidParticle = root_cuds_object.get(
            oclass=wet_synthesis.SolidParticle)[0]

        self._insert_data(
            'Density', solidParticle, 'crystal_density', dataDict)
        self._insert_data(
            'MolecularWeight', solidParticle, 'crystal_MW', dataDict)
        self._insert_data(
            'ShapeFactor', solidParticle, 'shape_factor', dataDict)

        for feed in root_cuds_object.get(oclass=wet_synthesis.Feed):
            self._insert_feed(feed, dataDict)

        conc_mixed_nh3 = self._mixed_conc(
            'nh3', 'nh3',
            root_cuds_object.get(oclass=wet_synthesis.Feed))

        dataDict.update({'conc_mixed_nh3': conc_mixed_nh3})

        if self._end_time is None:
            self._end_time = self._estimate_end_time(
                root_cuds_object.get(oclass=wet_synthesis.Feed), 0.00306639)
        self._end_time = 20
        dataDict.update({'end_time': self._end_time})

        if self._write_interval is None:
            self._write_interval = 1
        dataDict.update({'write_interval': self._write_interval})

        times = self._estimate_time_intervals()
        for i in range(np.size(times)):
            dataDict.update({'t{}'.format(i): times[i]})

        # replace the separator in the data based on the engine
        replace_char_in_keys(dataDict, "_", self._input_format["sep"])

        # Write the inputs in the include file
        self._write_dict(
            dataDict, "input", "cfdSimulation/include", "cfdSimulation/include_original")

        self._update_yaml("/compartmentSimulation/caseSetup.yml", solidParticle, root_cuds_object)

        self._add_division()

        self._initialized = True

    def _update_size_dist_cud(self, root_cuds_object):
        moments = self._extract_moments()

        if not self._dummy:
            print("Reconstructing the particle size distribution",
                  "with the following moments:\n", moments, "\n")

        else:  # This is used only for fast checking in the code development
            moments = [
                4.77253617e+13, 1.08819180e+08, 2.99624644e+02, 9.09160310e-04]
            print("Reconstructing the particle size distribution",
                  "with the following DUMMY moments:\n", moments, "\n")

        vol_percents, bin_sizes = reconstruct_log_norm_dist(moments)

        sizeDistribution = root_cuds_object.get(
            oclass=wet_synthesis.SizeDistribution)[0]

        for i, (vol_percent, bin_size) in \
                enumerate(zip(vol_percents, bin_sizes)):
            bin_i = wet_synthesis.Bin(number=i)
            bin_i.add(
                wet_synthesis.ParticleDiameter(
                    value=bin_size, unit='micrometer'),
                wet_synthesis.ParticleVolumePercentage(
                    value=vol_percent, unit=''),
                rel=wet_synthesis.hasPart)

            sizeDistribution.add(bin_i)

    def _extract_moments(self):
        """ Extract the average of moments at the outlet, which are
            already calculated and saved by engine """
        moments = list()

        if self._engine == "pisoPrecNMC":
            fluxPath = os.path.join(self._case_dir, 'compartmentSimulation', 'react_zone_flux.txt')
            fluxes = np.loadtxt(fluxPath, dtype=int, skiprows=2, usecols=(1, 3))
            for i in range(np.size(fluxes, axis=0)):
                if fluxes[i, 0] == fluxes[i, 1]:
                    outComp = fluxes[i, 0]
            output_path = os.path.join(
                self._case_dir, 'compartmentSimulation', 'timeResults', '0.01',
                'moments.npy')

            if os.path.isfile(output_path):
                data = np.load(output_path)
                moments = data[outComp, :].tolist()
            else:
                raise Exception()

        elif self._engine == "fluent":
            print("Not available yet for this engine")

        return moments

    def _update_compartment_cuds(self, root_cuds_object):

        zone_id, zone_ave, zone_volume, \
            origin_id, destination_id, flowrate, \
            boundary_name, boundary_destination, boundary_flowrate = \
            read_compartment_data(self._case_dir)

        compartmentNetwork = root_cuds_object.get(
            oclass=wet_synthesis.CompartmentNetwork)[0]

        for (id_i, ave_i, volume_i) in \
                zip(zone_id, zone_ave, zone_volume):

            compartment_i = wet_synthesis.Compartment(ID=id_i)
            compartment_i.add(
                wet_synthesis.Volume(value=volume_i, unit='m3'),
                wet_synthesis.TurbulentDissipationRate(
                    value=ave_i, unit='m2/s3'),
                rel=wet_synthesis.hasPart)

            compartmentNetwork.add(compartment_i)

        for (origin_id_i, destination_id_i, flowrate_i) in \
                zip(origin_id, destination_id, flowrate):

            compartment_i = find_compartment_by_id(
                origin_id_i, compartmentNetwork)

            if origin_id_i == destination_id_i:
                compartment_i.add(
                    wet_synthesis.OutletBoundaryFlux(value=flowrate_i,
                                                     unit='m3/s',
                                                     name='outlet'),
                    rel=wet_synthesis.hasPart)
            else:
                compartment_i.add(
                    wet_synthesis.OutgoingFlux(value=flowrate_i,
                                               unit='m3/s',
                                               ID=destination_id_i),
                    rel=wet_synthesis.hasPart)

        for (name_i, destination_i, flowrate_i) in \
                zip(boundary_name, boundary_destination, boundary_flowrate):

            compartment_i = find_compartment_by_id(
                destination_i, compartmentNetwork)

            compartment_i.add(
                wet_synthesis.InletBoundaryFlux(value=flowrate_i,
                                                unit='m3/s',
                                                name=name_i),
                rel=wet_synthesis.hasPart)

    def _check_logfile(self):
        """ Prints the log of the simulation to the standard output """
        sim_log_path = os.path.join(self._case_dir, "log.txt")

        with open(sim_log_path, "r") as logs:
            for line in logs:
                print(line)

    def _select_mesh(self, accuracy_level):

        refine_level = accuracy_level.number

        ''' currently there is only one mesh '''
        refine_level = 0

        mesh_info = self._mesh_info

        meshFileName = "{:s}_refinementLevel_{:d}.{:s}".format(
            mesh_info["name"], refine_level, mesh_info["ext"])

        return meshFileName

    def _insert_data(self, entityName, container, inputName, dataDict,
                     conversionFactor=1.0, attribute='value'):
        """ This function inserts new entries into the dataDict. No need to
            return the updated dictionary because it is passed by reference """
        entity = container.get(oclass=wet_synthesis.get(entityName))[0]

        inputValue = getattr(entity, attribute)

        dataDict.update(
            {
                inputName: inputValue * conversionFactor
            }
        )

        return inputValue

    def _insert_feed(self, feed, dataDict):

        inputName = "flowrate_" + feed.name
        self._insert_data(
            'FlowRate', feed, inputName, dataDict,
            conversionFactor=self._conversionFactors["FlowRate"])

        for component in feed.get(oclass=wet_synthesis.Component):
            inputName = "conc_in_" + component.name
            self._insert_data(
                'MolarConcentration', component, inputName, dataDict)

    def _mixed_conc(self, component_name, feed_name, feeds):

        total_flowrate = 0.0
        flowrate = None
        conc = None
        for feed in feeds:
            total_flowrate += feed.get(
                oclass=wet_synthesis.get('FlowRate'))[0].value

            if feed.name == feed_name:
                flowrate = feed.get(
                    oclass=wet_synthesis.get('FlowRate'))[0].value

                for component in feed.get(oclass=wet_synthesis.Component):
                    if component.name == component_name:
                        conc = component.get(oclass=wet_synthesis.get(
                            'MolarConcentration'))[0].value

        return conc * flowrate / total_flowrate

    def _estimate_end_time(self, feeds, reactor_volume):

        residence_time = self._residence_time(feeds, reactor_volume)

        end_time = 5*residence_time + 60

        # round the estimated end time
        if end_time > 1.0:
            exponent = max(min(math.floor(math.log10(end_time)) - 1, 2), 0)
            end_time = math.ceil(end_time / (10**exponent)) * (10**exponent)

        return end_time

    def _residence_time(self, feeds, reactor_volume):

        total_flowrate = 0.0
        for feed in feeds:
            total_flowrate += feed.get(
                oclass=wet_synthesis.get('FlowRate'))[0].value

        total_flowrate *= self._conversionFactors["FlowRate"]

        return reactor_volume / total_flowrate

    def _estimate_time_intervals(self):

        cfd_time = 60

        times = np.zeros(14)

        # times[0] = 10
        # times[1] = 30
        # times[2] = cfd_time - 0.01
        # times[3] = cfd_time + self._end_time/3
        times[0] = 8

        return times

    def _write_dict(self, dataDict, file_name, folder, template_folder):
        """Fill in a templated input file with provided parameters"""
        # Path to the template file
        template_path = os.path.join(
            self._case_dir, template_folder, file_name)

        # Path to the file
        file_path = os.path.join(
            self._case_dir, folder, file_name)

        input_format = self._input_format

        with open(template_path, "r") as template:
            with open(file_path, "w") as f:
                for line in template:
                    key = line.split()[0] if line.split() else None
                    if key in dataDict:
                        line = "%s %s%s" % (
                            key, dataDict[key], input_format["end"])
                        del dataDict[key]
                    print(line.strip(), file=f)
                for key, value in dataDict.items():
                    print("%s%s %s%s" % (input_format["begin"], key, value,
                                         input_format["end"]), file=f)

    def _update_yaml(self, file_name, solidParticle, root):
        """Modify yaml file caseSetup.yml for compartment simulation"""
        
        _temp = root.get(oclass=wet_synthesis.get("Temperature"))[0]
        temp = getattr(_temp, 'value')

        _density = solidParticle.get(oclass=wet_synthesis.get("Density"))[0]
        density = getattr(_density, 'value')

        _MW = solidParticle.get(oclass=wet_synthesis.get("MolecularWeight"))[0]
        MW = getattr(_MW, 'value')

        _KV = solidParticle.get(oclass=wet_synthesis.get("ShapeFactor"))[0]
        KV = getattr(_KV, 'value')

        nodes = self._num_moments / 2

        concs = np.zeros(6)
        for i, component in enumerate(root.get(oclass=wet_synthesis.Component)):
            inputName = "conc_in_" + component.name
            concs[i] = component.get(oclass=wet_synthesis.get(inputName))[0]
        print(concs)
        
        f = open(self._case_dir+file_name, 'r')
        lines = f.readlines()
        f.close()

        for i, line in enumerate(lines):
            if 'T: 0' in line:
                lines[i] = line.replace('0', str(temp))
            if 'density: 0' in line:
                lines[i] = line.replace('0', str(density))
            if 'numOfNodes: 0' in line:
                lines[i] = line.replace('0', str(nodes))
            if 'metals:' in line:
                string = '['+str(concs[0])+', '+str(concs[1])+', '+str(concs[2])+', 0.0, 0.0, '+str(concs[3])+']'
                lines[i+1] = line.replace('[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]', string)
            if 'nh3:' in line:
                string = '[0.0, 0.0, 0.0, '+str(concs[4])+', 0.0, 0.0]'
                lines[i+1] = line.replace('[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]', string)
            if 'naoh:' in line:
                string = '[0.0, 0.0, 0.0, 0.0, '+str(concs[-1])+', 0.0]'
                lines[i+1] = line.replace('[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]', string)

        with open(self._case_dir+file_name, 'w') as f:
            f.writelines(lines)
            f.close()

        f = open(self._case_dir+'/importScripts/NiMnCoHydroxidePrec.py', 'r')
        lines2 = f.readlines()
        f.close()
        for i, line in enumerate(lines2):
            if 'self.kv = math.pi / 6' in line:
                lines2[i] = line.replace('math.pi / 6', str(KV))
        with open(self._case_dir+'/importScripts/NiMnCoHydroxidePrec.py', 'w') as f:
            f.writelines(lines2)
            f.close()

        f = open(self._case_dir+'/importScripts/init_run.py', 'r')
        lines3 = f.readlines()
        f.close()
        for i, line in enumerate(lines3):
            if 'aMassCrystal = _MW' in line:
                lines3[i] = line.replace('_MW', str(MW))
        with open(self._case_dir+'/importScripts/init_run.py', 'w') as f:
            f.writelines(lines3)
            f.close()
 
        
    def _add_division(self):
        """Copy file for reactor division and update time directory"""

        # Directory of files for reactor division
        division_dir = "/home/simdomeuser/wet-synthesis-route/reactor_network_model/reactor_division/"
        target_dir = self._case_dir+'/compartmentSimulation/'

        name_list = ['reactDivision', 'extract_info.py', 'react_division.py', 'importScripts/read_files.py']
        dir_list = ['', '', '', 'importScripts/']

        for (name, directory) in zip(name_list, dir_list):
            shutil.copy(division_dir+name, target_dir+directory)
            f = open(target_dir+name, 'r')
            lines = f.readlines()
            f.close()

            for i, line in enumerate(lines):
                if "time_dir = '0'" in line:
                    lines[i] = line.replace("0", str(self._end_time))
            
            with open(target_dir+name, 'w') as file:
                file.writelines(lines)


    def engine_specialization(self, engine):
        if engine == "pisoPrecNMC":
            self._case_template = os.path.join(
                self._case_source, "precNMC_compartmentTemplate")

            self._exec = ["./Allrun", str(self._num_proc)]

            self._mesh_info = {"name": "polyMesh", "ext": "zip"}

            self._input_format = {"begin": "", "end": ";", "sep": "_"}

            self._conversionFactors = {
                "RotationalSpeed": math.pi/30,
                "FlowRate": 1.0/3.6e6}

        else:
            raise Exception("\nEngine \"" + engine + "\" not available\n")
