import os
import subprocess
import shutil
import math

from osp.core.session import SimWrapperSession
from osp.core.namespaces import wet_synthesis
from osp.wrappers.wet_synthesis_wrappers.utils import read_compartment_data
from osp.wrappers.wet_synthesis_wrappers.utils import find_compartment_by_id


class CompartmentSession(SimWrapperSession):
    """
    Session class for compartment model
    """

    def __init__(self, engine="fluent", case="precNMC",
                 delete_simulation_files=True, **kwargs):
        super().__init__(engine, **kwargs)

        # Whether or not to store the generated files by the simulation engine
        self._delete_simulation_files = delete_simulation_files

        # Engine specific initializations
        self._initialized = False
        self._case_template = os.path.join(
            os.path.dirname(__file__), "cases", case, "precNMC_fluentTemplate")
        self._mesh_files = os.path.join(
            os.path.dirname(__file__), "cases", case, "meshFiles")
        self._case_dir = None

        # Set engine defaults
        self._end_time = 10

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
            # print("\n{} job started\n".format(self._engine))
            # retcode = subprocess.call(
            #     ["fluent", "3d", "-cflush", "-g", "-t", "4",
            #      "-i", "precNMC.jou"],
            #     cwd=self._case_dir)

            # The engine execution is disabled intentionally since
            # the mesh files and the solver are not provided
            print("\nDummy job started\n")
            retcode = 0

            if retcode == 0:
                # print("\n{} job finished successfully\n".format(self._engine))
                print("\nDummy job finished\n")
            else:
                print("\n{} job terminated with exit code {:d}\n".format(
                    self._engine, retcode))

            self._update_compartment_cuds(root_cuds_object)
            print("Compartment data is updated\n")

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

        input_dir = os.path.join(self._case_dir, 'include')
        os.makedirs(input_dir, exist_ok=True)

        # Extract data from CUDS
        accuracy_level = root_cuds_object.get(
            oclass=wet_synthesis.SliderAccuracyLevel)[0]

        # Select the mesh based on the accuracy level
        meshFileName = self._select_mesh(accuracy_level)

        # Copy the mesh file
        meshSourcePath = os.path.join(self._mesh_files, meshFileName)
        if os.path.isfile(meshSourcePath):
            shutil.copy(meshSourcePath, self._case_dir)
        else:
            raise Exception()

        # Dictionary to insert the inputs
        dataDict = dict()

        # add the material
        # material = root_cuds_object.get(oclass=wet_synthesis.Material)[0]

        # Insert pressure into the input dictionary
        self._insert_data(
            'Pressure', root_cuds_object, 'outlet-pressure', dataDict)

        # Insert rotational speed into the input dictionary
        self._insert_data(
            'RotationalSpeed', root_cuds_object, 'impeller-angular-velocity',
            dataDict)

        for feed in root_cuds_object.get(oclass=wet_synthesis.Feed):
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
            dataDict, "input.scm", "include", "include_original")

        self._initialized = True

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

        # Select mesh based on the accuracy level
        if 5 < refine_level and refine_level <= 10:
            meshFileName = 'mesh_refinementLevel_{:d}.msh'.format(
                refine_level)
        else:
            # The values stored in the slider accuracy level should be
            # from 6 to 10
            meshFileName = None

        # This line will be removed when all grids are prepared
        meshFileName = 'mesh_refinementLevel_6.msh'

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

        inputName = "flowrate-" + feed.name
        self._insert_data(
            'FlowRate', feed, inputName, dataDict, conversionFactor=1/3.6e6)

    def _write_dict(self, dataDict, file_name, folder, template_folder):
        """Fill in a templated scheme file with provided parameters"""
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
                        line = "%s %s)" % (key, dataDict[key])
                        del dataDict[key]
                    print(line.strip(), file=f)
                for key, value in dataDict.items():
                    print("(define %s %s)" % (key, value), file=f)
