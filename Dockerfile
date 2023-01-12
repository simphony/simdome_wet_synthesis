ARG OSP_CORE_IMAGE=simphony/osp-core:latest
FROM $OSP_CORE_IMAGE
LABEL maintainer="mohsen.shiea@polito.it"
LABEL dockerfile.version="1.1"

# Install requirements
RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    git graphviz wget build-essential g++ gfortran libgfortran5 openmpi-bin libopenmpi-dev make libssl-dev libblas-dev liblapack-dev \
    apt-transport-https software-properties-common openssh-client bash-completion bash-builtins libnss-wrapper vim nano tree curl unzip

ENV CONDA_DIR /opt/conda
RUN wget -c https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh -O ~/conda.sh && \
    /bin/bash ~/conda.sh -bfp /opt/conda && \
    conda update conda && conda create --name compartment && conda install mkl-service
ENV PATH=$CONDA_DIR/bin:$PATH

RUN cd / && mkdir cmake && cd cmake && \
    CMAKE_VERSION=3.20.1 && \
    wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz && \
    tar -zxvf cmake-${CMAKE_VERSION}.tar.gz && \
    cd cmake-${CMAKE_VERSION} && \
    ./bootstrap && \
    make -j $(nproc) && \
    make install && \
    cd / && rm -r cmake

RUN cd / && mkdir sundials && cd sundials && \
    CVODE_VERSION=6.1.1 && \
    wget https://github.com/LLNL/sundials/releases/download/v${CVODE_VERSION}/cvode-${CVODE_VERSION}.tar.gz && \
    tar -zxvf cvode-${CVODE_VERSION}.tar.gz && \
    mkdir instdir && \
    mkdir builddir && cd builddir && \
    cmake -DCMAKE_INSTALL_PREFIX=/sundials/instdir -DEXAMPLES_INSTALL_PATH=/sundials/instdir/examples -DENABLE_MPI=ON -S ../cvode-${CVODE_VERSION} && \
    make -j $(nproc) && \
    make install && \
    cd .. && rm -r builddir cvode-${CVODE_VERSION} cvode-${CVODE_VERSION}.tar.gz

RUN cd /usr/bin && rm python3 && ln -s python3.6 python3 && \
    wget -O - http://dl.openfoam.org/gpg.key | apt-key add - && add-apt-repository http://dl.openfoam.org/ubuntu && \
    apt-get update && apt-get install -y --no-install-recommends openfoam8 && \
    cd /usr/bin && rm python3 && ln -s python3.7 python3 && rm -rf /var/lib/apt/lists/*

ENV user=simdomeuser HOME=/home/simdomeuser

RUN useradd --user-group --create-home --shell /bin/bash --no-log-init $user

USER $user

RUN ["/bin/bash", "-c", "source /opt/openfoam8/etc/bashrc && mkdir -p $FOAM_USER_APPBIN && mkdir -p $FOAM_USER_LIBBIN && \
    cd $HOME && git clone https://github.com/mulmopro/wet-synthesis-route.git && \
    cd wet-synthesis-route/cfd_pbe_openfoam_solver && \
    if [ \"$(cat /etc/os-release | grep VERSION_ID | perl -pe '($_)=/([0-9]+([.][0-9]+)+)/' | perl -pe '($_)=/([0-9]+)/')\" -eq \"18\" ]; \
    then sed -i -e 's/nMetals, nMoments, nY, nCells, odeEndTime, //g' precSource.H; fi && ./Allwmake -j $(nproc) && \
    cd $HOME/wet-synthesis-route/cfd_onlyEnv && ./Allwmake -j $(nproc)"]

RUN mkdir -p $HOME/simdome/wrappers/simdome_wet_synthesis && \
    chown -R $user:$user $HOME/simdome/wrappers/simdome_wet_synthesis
COPY --chown=$user . $HOME/simdome/wrappers/simdome_wet_synthesis
WORKDIR $HOME/simdome/wrappers/simdome_wet_synthesis

ENV PATH=$PATH:$HOME/.local/bin

RUN pip install matplotlib scipy mpi4py \
    && pico install ontology.wet_synthesis.yml \
    && python setup.py install --user

CMD ["/bin/bash", "-c", "source /opt/openfoam8/etc/bashrc && /bin/bash && source activate compartment" ]
