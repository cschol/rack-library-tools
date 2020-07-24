#!/bin/bash

# EXAMPLE build script to build plugin for all platforms and validate plugin manifest.

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

# Root directory of the plugin repository (e.g. library-v1/repos or Rack/plugins)
PLUGIN_ROOT=$1

# Name of plugin (i.e. directory name in library)
PLUGIN_NAME=$2

# Rack-SDK to compile libraries
export RACK_DIR=/home/cschol/src/Rack-SDK/Rack-SDK

# Windows
CC=x86_64-w64-mingw32-gcc \
CXX=x86_64-w64-mingw32-g++ \
STRIP=x86_64-w64-mingw32-strip \
python3 ${SCRIPTPATH}/vcv-plugin-builder.py ${PLUGIN_ROOT} -p ${PLUGIN_NAME} --platforms win

# Mac
PATH=${PATH}:/home/cschol/src/osxcross/target/bin \
CC=x86_64-apple-darwin17-clang \
CXX=x86_64-apple-darwin17-clang++ \
STRIP=x86_64-apple-darwin17-strip \
LD_LIBRARY_PATH="/home/cschol/src/osxcross/target/lib" \
python3 ${SCRIPTPATH}/vcv-plugin-builder.py ${PLUGIN_ROOT} -p ${PLUGIN_NAME} --platforms mac

# Linux
docker run \
    -e RACK_DIR=/workdir/Rack-SDK \
    -v ${RACK_DIR}:/workdir/Rack-SDK \
    -v ${PLUGIN_ROOT}:/workdir/repos \
    -v ${PWD}:/workdir \
    vcvrack/linux-plugin-build \
    /bin/bash \
    -c "python3 /workdir/vcv-plugin-builder.py /workdir/repos -p ${PLUGIN_NAME} --platforms linux"

# Validate manifest
python3 ${SCRIPTPATH}/vcv-manifest-validator.py ${PLUGIN_ROOT} -p ${PLUGIN_NAME}
