#!/bin/bash

# EXAMPLE build script to build plugin for all platforms and validate plugin manifest.

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

# Root directory of the plugin repository (e.g. library-v1/repos or Rack/plugins)
PLUGIN_ROOT=$1

# Name of plugin (i.e. directory name in library)
PLUGIN_NAME=$2

# System-specific locations of libraries used by build process
# For cross-compilation of Mac platform on Linux
OSXCROSS=/home/cschol/src/osxcross
# Rack-SDK to compile libraries
RACK_SDK=/home/cschol/src/Rack-SDK/Rack-SDK

# Windows
python3 ${SCRIPTPATH}/vcv-plugin-builder.py ${RACK_SDK} ${PLUGIN_ROOT} --clean -p ${PLUGIN_NAME} --platforms win

# Mac
python3 ${SCRIPTPATH}/vcv-plugin-builder.py ${RACK_SDK} ${PLUGIN_ROOT} --osxcrosslib ${OSXCROSS}/target/lib --clean -p ${PLUGIN_NAME} --platforms mac

# Linux
docker run -v ${RACK_SDK}:/workdir/Rack-SDK -v ${PLUGIN_ROOT}:/workdir/repos -v ${PWD}:/workdir vcvrack/linux-plugin-build /bin/bash -c "/usr/bin/python3 /workdir/vcv-plugin-builder.py /workdir/Rack-SDK /workdir/repos --clean -p ${PLUGIN_NAME} --platforms linux"

# Validate manifest
python3 ${SCRIPTPATH}/vcv-manifest-validator.py ${PLUGIN_ROOT} -p ${PLUGIN_NAME} --check-version

