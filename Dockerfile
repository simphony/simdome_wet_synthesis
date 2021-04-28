ARG OSP_CORE_IMAGE=simphony/osp-core:latest
FROM $OSP_CORE_IMAGE
LABEL maintainer="mohsen.shiea@polito.it"
LABEL dockerfile.version="1.0"

ADD . /simdome/wrappers/simdome_wet_synthesis
WORKDIR /simdome/wrappers/simdome_wet_synthesis

# Install requirements
RUN apt update && apt install -y \
    git graphviz p7zip p7zip-full

RUN pip install matplotlib \
    && pico install ontology.wet_synthesis.yml \
    && python setup.py install
