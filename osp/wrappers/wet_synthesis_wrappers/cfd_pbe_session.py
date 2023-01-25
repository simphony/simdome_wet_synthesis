import os
import subprocess
import shutil
import math
import numpy as np

from osp.core.session import SimWrapperSession
from osp.core.namespaces import wet_synthesis
from osp.wrappers.wet_synthesis_wrappers.utils import reconstruct_log_norm_dist
from osp.wrappers.wet_synthesis_wrappers.utils import replace_char_in_keys


class CfdPbeSession(SimWrapperSession):
    """
    Session class for pisoPrecNMC solver
    """

    def __init__(self, engine="pisoPrecNMC", case="precNMC",
                 delete_simulation_files=True, **kwargs):
        
        self._engine = engine

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
        return "A session for NMC hydroxide precipitation CFD-PBE solver"

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
            retcode = subprocess.call(self._exec, cwd=self._case_dir)

            if retcode == 0:
                print("\n{} finished successfully\n".format(self._engine))

                self._update_size_dist_cud(root_cuds_object)
                print("Particle size distribution is updated\n")
            else:
                print("\n{} terminated with exit code {:d}\n".format(
                    self._engine, retcode))

    # OVERRIDE
    def _load_from_backend(self, uids, expired=None):
        """ Loads the cuds object from the simulation engine """
        for uid in uids:
            try:
                yield self._registry.get(uid)
            except KeyError:
                yield None

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
            os.getcwd(), "simulation-wetSynthCfdPbe-%s" % root_cuds_object.uid)
        shutil.copytree(self._case_template, self._case_dir)

        if self._engine == "fluent":
            division_dir = "$HOME/wet-synthesis-route/cfd_pbe_fluent_udf/Linux/"
            name_list = ['precNMC_sources.c', 'precNMC_adjust.c', 'headerFiles/chemicalEquilibria.h', 'headerFiles/defMacros.h', 'headerFiles/externFuncs.h', 'headerFiles/externVars.h', 'headerFiles/momentCalc.h', 'headerFiles/particleProcesses.h']
            for name in name_list:
                shutil.copytree(division_dir+name, self._case_dir)

        # constant_dir = os.path.join(self._case_dir, 'constant')
        input_dir = os.path.join(self._case_dir, 'include')
        os.makedirs(input_dir, exist_ok=True)

        # Extract data from CUDS
        accuracy_level = root_cuds_object.get(
            oclass=wet_synthesis.SliderAccuracyLevel)[0]

        # Select the mesh based on the accuracy level
        meshFileName = self._select_mesh(accuracy_level)

        meshSourcePath = os.path.join(
            self._case_source, "meshFiles", meshFileName)

        meshTargerPath = os.path.join(
            self._case_dir, "{:s}.{:s}".format(self._mesh_info["name"],
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

        # Insert liquid density into the input dictionary
        self._insert_data(
            'LiquidDensity', root_cuds_object, 'liquid_density', dataDict)

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
                root_cuds_object.get(oclass=wet_synthesis.Feed), 0.00306639) + 60
        else:
            self._end_time = self._end_time + 60
        if self._dummy:
            self._end_time = 0.0011
        dataDict.update({'end_time': self._end_time})

        if self._write_interval is None:
            if self._dummy:
                self._write_interval = 1
            else:
                self._write_interval = 100
        dataDict.update({'write_interval': self._write_interval})

        times = self._estimate_time_intervals()
        for i in range(np.size(times)):
            dataDict.update({'t{}'.format(i): times[i]})

        # replace the separator in the data based on the engine
        replace_char_in_keys(dataDict, "_", self._input_format["sep"])

        if self._engine == "pisoPrecNMC":
            # Write the inputs in the include file
            self._write_dict(
                dataDict, "input", "include", "include_original")
        else:
            # Modify files precNMC.scm, precNMC.jou and defMacros.h
            self._add_input(dataDict)

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

        vol_percents, bin_sizes = reconstruct_log_norm_dist(moments, self._num_moments)

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
            if self._dummy:
                output_path = os.path.join(
                    self._case_dir, 'postProcessing', 'outlet_average', '0.000992992',
                    'surfaceFieldValue.dat')
            else:
                output_path = os.path.join(
                    self._case_dir, 'postProcessing', 'outlet_average', '60',
                    'surfaceFieldValue.dat')

            if os.path.isfile(output_path):
                data = np.loadtxt(output_path, skiprows=4, unpack=False)
                moments = data[-1, 1:self._num_moments + 1].tolist()
            else:
                raise Exception()

        elif self._engine == "fluent":
            print("Not available yet for this engine")

        return moments

    def _check_logfile(self):
        """ Prints the log of the simulation to the standard output """
        if self._engine == "pisoPrecNMC":
            sim_log_path = os.path.join(self._case_dir, "log.txt")

            with open(sim_log_path, "r") as logs:
                for line in logs:
                    print(line)
        else:
            print("Not implemented for the selected engine")

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

        if self._engine == 'fluent':
            inputName = "velocity_" + feed.name
            self._insert_data(
                'FlowRate', feed, inputName, dataDict,
                conversionFactor=self._conversionFactors["InletVelocity_{}".format(feed.name)])
        else:
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

        end_time = 5*residence_time

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

        if self._dummy:
            times[0] = 0.001
        else:
            times[0] = 10
            times[1] = 30
            times[2] = cfd_time
            times[3] = cfd_time + 0.009981
            times[4] = cfd_time + 0.05991
            times[5] = cfd_time + 0.19981
            times[6] = cfd_time + 0.9991
            times[7] = cfd_time + 2.9981
            times[8] = cfd_time + 12.991
            times[9] = cfd_time + 34.981
            times[10] = cfd_time + 84.961
            times[11] = cfd_time + 249.921
            times[12] = cfd_time + 549.881
            times[13] = cfd_time + 999.841

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
                    
    def _add_input(self, dataDict):

        file_list = ["precNMC.scm", "precNMC.jou"]

        for key, value in dataDict.items():
            for fileName in file_list:
                path = self._case_dir+fileName
                f = open(path, 'r')
                lines=f.readlines()
                f.close()

                for i, line in enumerate(lines):
                    if key in line:
                        lines[i] = line.replace(key, value)

                with open(path, 'w') as f:
                    f.writelines(lines)

        f = open(self._case_dir+"defMacros.h", 'r')
        lines=f.readlines()
        f.close()

        for i, line in enumerate(lines):
            if '298.15' in line:
                lines[i] = line.replace('298.15', dataDict['temperature'])
            if '3953' in line:
                lines[i] = line.replace('3953', dataDict['crystal_density'])
            if '92.3383' in line:
                lines[i] = line.replace('92.3383', dataDict['crystal_MW'])
            if '0.523599' in line:
                lines[i] = line.replace('0.523599', dataDict['shape_factor'])

        with open (self._case_dir+"defMacros.h", 'w') as f:
            f.writelines(lines)


    def engine_specialization(self, engine):
        if engine == "pisoPrecNMC":
            if self._dummy:
                self._case_template = os.path.join(
                    self._case_source, "precNMC_foamTemplate_dummy")
            else:
                self._case_template = os.path.join(
                    self._case_source, "precNMC_foamTemplate")

            self._exec = ["./Allrun", str(self._num_proc)]

            self._mesh_info = {"name": "polyMesh", "ext": "zip"}

            self._input_format = {"begin": "", "end": ";", "sep": "_"}

            self._conversionFactors = {
                "RotationalSpeed": math.pi/30,
                "FlowRate": 1.0/3.6e6}

        elif engine == "fluent":
            self._case_template = os.path.join(
                self._case_source, "precNMC_fluentTemplate")

            self._exec = [
                "fluent", "3d", "-g", "-t", str(self._num_proc), "-i",
                "precNMC.jou"]

            self._mesh_info = {"name": "mesh_fluent", "ext": "msh.gz"}

            self._input_format = {"begin": "", "end": ";", "sep": "_"}

            self._conversionFactors = {
                "RotationalSpeed": 1.0,
                "InletVelocity_metals": 1.0/(3.6*6.9890206),
                "InletVelocity_naoh": 1.0/(3.6*7.0185032),
                "InletVelocity_nh3": 1.0/(3.6*7.0185032),
                "FlowRate": 1.0/3.6e6}

        else:
            raise Exception("\nEngine \"" + engine + "\" not available\n")
