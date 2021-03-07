import os
import subprocess
import shutil
import math

from osp.core.session import SimWrapperSession
from osp.core.namespaces import prec_nmc
from osp.wrappers.prec_nmc_wrappers.utils import reconstruct_log_norm_dist


class PrecFoamSession(SimWrapperSession):
    """
    Session class for simpleFoamPrecNMC solver
    """

    def __init__(self, engine="simpleFoamPrecNMC", case="precNMC",
                 delete_simulation_files=True, **kwargs):
        super().__init__(engine, **kwargs)

        # Whether or not to store the generated files by the simulation engine
        self._delete_simulation_files = delete_simulation_files

        # Engine specific initializations
        self._initialized = False
        self._case_template = os.path.join(
            os.path.dirname(__file__), "cases", case, "precNMC_foamTemplate")
        self._mesh_files = os.path.join(
            os.path.dirname(__file__), "cases", case, "meshFiles")
        self._case_dir = None

        # Set engine defaults
        self._end_time = 2
        self._write_interval = 1

        self._num_moments = 4

    def __str__(self):
        return "OpenFoam session for NMC hydroxide precipitation solver"

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
            # print("\n{} started\n".format(self._engine))
            # retcode = subprocess.call(
            #     [os.path.join(self._case_dir, "Allrun"), "1"],
            #     cwd=self._case_dir)

            # The engine execution is disabled intentionally since
            # the mesh files and the solver are not provided
            print("\nDummy job started\n")
            retcode = 0

            if retcode == 0:
                # print("\n{} finished successfully\n".format(self._engine))
                print("\nDummy job finished\n")
            else:
                print("\n{} terminated with exit code {:d}\n".format(
                    self._engine, retcode))

            self._update_size_dist_cud(root_cuds_object)
            print("Particle size distribution is updated\n")

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
            os.getcwd(), "simulation-precfoam-%s" % root_cuds_object.uid)
        shutil.copytree(self._case_template, self._case_dir)

        constant_dir = os.path.join(self._case_dir, 'constant')
        input_dir = os.path.join(self._case_dir, 'include')
        os.makedirs(input_dir, exist_ok=True)

        # Extract data from CUDS
        accuracy_level = root_cuds_object.get(
            oclass=prec_nmc.SliderAccuracyLevel)[0]

        # Select the mesh based on the accuracy level
        meshFileName = self._select_mesh(accuracy_level)

        # Copy the mesh file
        meshSourcePath = os.path.join(self._mesh_files, meshFileName)
        if os.path.isfile(meshSourcePath):
            shutil.copy(meshSourcePath, constant_dir)
        else:
            raise Exception()

        # Extract the files from .7z file, if it exists
        meshFilePath = os.path.join(constant_dir, meshFileName)
        if os.path.isfile(meshFilePath):
            subprocess.run(
                ["7z", "x", meshFileName], check=True, cwd=constant_dir)
        else:
            raise Exception()

        # Dictionary to insert the inputs
        dataDict = dict()

        # add the material
        # material = root_cuds_object.get(oclass=prec_nmc.Material)[0]

        # Insert pressure into the input dictionary
        self._insert_data(
            'Pressure', root_cuds_object, 'outlet_pressure', dataDict)

        # Insert temperature into the input dictionary
        self._insert_data(
            'Temperature', root_cuds_object, 'temperature', dataDict)

        # Insert rotational speed into the input dictionary
        self._insert_data(
            'RotationalSpeed', root_cuds_object, 'angular_velocity', dataDict,
            conversionFactor=math.pi/30)

        # Add the particle properties to the input dictionary
        solidParticle = root_cuds_object.get(oclass=prec_nmc.SolidParticle)[0]

        self._insert_data(
            'Density', solidParticle, 'crystal_density', dataDict)
        self._insert_data(
            'MolecularWeight', solidParticle, 'crystal_MW', dataDict)
        self._insert_data(
            'ShapeFactor', solidParticle, 'shape_factor', dataDict)

        for feed in root_cuds_object.get(oclass=prec_nmc.Feed):
            self._insert_feed(feed, dataDict)

        # # check if setfieldsDict exists and then run it
        # setFieldsDictPath = os.path.join(
        #     self._case_dir, "system", "setFieldsDict")

        # if os.path.isfile(setFieldsDictPath):
        #     subprocess.run("setFields", check=True, cwd=self._case_dir)

        # # Set controlDict parameters
        # control_params = dict()
        # control_params["writeInterval"] = self._write_interval
        # control_params["deltaT"] = self._delta_time

        # # Write the controlDict dictionary
        # self._write_dict(
        #     control_params, "controlDict", "system", "system_original")

        # Write the inputs in the include file
        self._write_dict(
            dataDict, "input", "include", "include_original")

        self._initialized = True

    def _update_size_dist_cud(self, root_cuds_object):
        moments = self._extract_moments()

        print("Reconstructing the particle size distribution",
              "with the following moments:\n", moments, "\n")

        vol_percents, bin_sizes = reconstruct_log_norm_dist(moments)

        sizeDistribution = root_cuds_object.get(
            oclass=prec_nmc.SizeDistribution)[0]

        for i, (vol_percent, bin_size) in \
                enumerate(zip(vol_percents, bin_sizes)):
            bin_i = prec_nmc.Bin(number=i)
            bin_i.add(
                prec_nmc.ParticleDiameter(value=bin_size, unit='micrometer'),
                prec_nmc.ParticleVolumePercentage(value=vol_percent, unit=''),
                rel=prec_nmc.hasPart)

            sizeDistribution.add(bin_i)

    def _extract_moments(self):
        """ Extract the average of moments at the outlet, which are
            already calculated and saved by engine """
        output_path = os.path.join(
            self._case_dir, 'postProcessing', 'outletAverage', '0',
            'surfaceFieldValue.dat')

        moments = list()
        if os.path.isfile(output_path):
            with open(output_path, "r") as f:
                for line in f:
                    key = line.split()[0] if line.split() else None
                    if key == str(self._end_time):
                        data_string = line.split()[1:]
                        for i in range(len(data_string)):
                            moments.append(float(data_string[i]))
                        break
        else:
            raise Exception()

        return moments

    def _check_logfile(self):
        """ Prints the log of the simulation to the standard output """
        sim_log_path = os.path.join(self._case_dir, "log.txt")

        with open(sim_log_path, "r") as logs:
            for line in logs:
                print(line)

    def _select_mesh(self, accuracy_level):

        refine_level = accuracy_level.number

        # Select mesh based on the accuracy level
        if 5 < refine_level and refine_level <= 10:
            meshFileName = 'polyMesh_refinementLevel_{:d}.7z'.format(
                refine_level)
        else:
            # The values stored in the slider accuracy level should be
            # from 6 to 10
            meshFileName = None

        # This line will be removed when all grids are prepared
        meshFileName = 'polyMesh_refinementLevel_6.7z'

        return meshFileName

    def _insert_data(self, entityName, container, inputName, dataDict,
                     conversionFactor=1.0, attribute='value'):
        """ This function inserts new entries into the dataDict. No need to
            return the updated dictionary because it is passed by reference """
        entity = container.get(oclass=prec_nmc.get(entityName))[0]

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
            'FlowRate', feed, inputName, dataDict, conversionFactor=1/3.6e6)

        total_conc = 0.0
        for component in feed.get(oclass=prec_nmc.Component):
            inputName = "conc_in_" + component.name
            conc = self._insert_data(
                'MolarConcentration', component, inputName, dataDict)
            total_conc += conc

        if feed.name == 'metals':
            dataDict.update(
                {
                    'conc_in_inertCharge_metals': -2.0*total_conc
                }
            )
        elif feed.name == 'naoh':
            dataDict.update(
                {
                    'conc_in_inertCharge_naoh': total_conc
                }
            )
        else:
            pass

    def _write_dict(self, dataDict, file_name, folder, template_folder):
        """Fill in a templated dictionary file with provided parameters"""
        # Path to the template file
        template_path = os.path.join(
            self._case_dir, template_folder, file_name)

        # Path to the file
        file_path = os.path.join(
            self._case_dir, folder, file_name)

        with open(template_path, "r") as template:
            with open(file_path, "w") as f:
                for line in template:
                    key = line.split()[0] if line.split() else None
                    if key in dataDict:
                        line = "%s %s;" % (key, dataDict[key])
                        del dataDict[key]
                    print(line.strip(), file=f)
                for key, value in dataDict.items():
                    print("%s %s;" % (key, value), file=f)
