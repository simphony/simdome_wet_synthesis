#!/bin/bash
#
# Description: This script creates a docker image that includes the osp-core
#              and the wet synthesis wrappers
#
# Run Information: This script should be run manually.


# Extract osp-version
osp_tag="v"
osp_tag+="$(python3 -c 'import packageinfo; print(packageinfo.OSP_CORE_MIN)')"
# osp_tag+="-beta"

rm -rf temp_osp-core | true
# Download osp-core to temporary folder
git clone https://github.com/simphony/osp-core.git temp_osp-core

cd temp_osp-core
git checkout ${osp_tag}
docker build -t simphony/osp-core:${osp_tag} .

ERROR_CODE=$?
if [ $ERROR_CODE -ne 0 ]; then
    echo -e "\nError:"
    echo -e "osp-core image creation failed.\n" >&2

    cd ..
    rm -rf temp_osp-core | true

    exit $ERROR_CODE
fi

cd ..
rm -rf temp_osp-core | true

# Build docker image
docker build -t simdome/wet_synthesis --build-arg OSP_CORE_IMAGE=simphony/osp-core:${osp_tag} .
