#!/bin/bash

CONTAINER_NAME=wet-synthesis

docker container inspect -f '{{.State.Status}}' $CONTAINER_NAME > /dev/null 2>&1

if [ "$?" = "0" ]; then
    docker exec -it $CONTAINER_NAME bash -c ". ~/.bashrc ; $ARGS"
else
    docker run -it --rm --hostname=SIMDOME \
        --cap-drop=ALL --security-opt=no-new-privileges \
        --cap-add=SYS_PTRACE \
        --name $CONTAINER_NAME simdome/wet_synthesis:latest
fi
