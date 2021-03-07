#!/bin/bash
#
# Description: This script creates a docker image that includes the osp-core
#              and the prec_nmc wrappers
#
# Run Information: This script should be run manually.


# Extract osp-version
osp_tag="v"
osp_tag+="$(python3 -c 'import packageinfo; print(packageinfo.OSP_CORE_MIN)')"
osp_tag+="-beta"

rm -rf temp_osp-core | true
# Download osp-core to temporary folder
git clone https://github.com/simphony/osp-core.git temp_osp-core
# Replace the original Dockerfile to omit the procedures related to tox
cp Dockerfile_osp_core temp_osp-core/Dockerfile

cd temp_osp-core
git checkout ${osp_tag}
docker build -t simphony/osp-core:${osp_tag} .
cd ..
rm -rf temp_osp-core | true

# Build docker image
docker build -t simdome/prec_nmc --build-arg OSP_CORE_IMAGE=simphony/osp-core:${osp_tag} .
