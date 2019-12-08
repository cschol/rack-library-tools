# VCV Library Tools

Set of tools I use to manage integration of plugins into the VCV Rack `library` repository.

- vcv-manifest-validator.py
- vcv-plugin-builder.py

## General Notes

These tools are specifically written to run on **GNU/Linux**, which is the system I use mostly for integration of plugins in the Plugin Manager.
These tools are written to operate on a local working copy of the Rack [library repository](https://github.com/VCVRack/library).

The `Linux` platform is build in a `Docker` container to ensure compatibility with the Rack build system.

The `Dockerfile` contains the recipe to build the Docker image, which can be used to build the Linux platform.
See section below on how to build the Docker image.

## Manifest Validator - `vcv-manifest-validator.py`

Script to automate batch and individual validation of `plugin.json` manifest(s).

```
python3 ./vcv-manifest-validator.py <RACK_SOURCE_DIR> <LIBRARY_REPO_ROOT> [-p SPECIFIC_PLUGIN_TO_VALIDATE] [--check-version]
```

Examples:

- Validate **all** plugin manifests:

```
python3 ./vcv-manifest-validator.py /home/cschol/src/Rack-1.0 /home/cschol/src/library/repos --check-version
```

- Validate individual manifest for `modular80`:

```
python3 ./vcv-manifest-validator.py /home/cschol/src/Rack-1.0 /home/cschol/src/library/repos -p modular80 --check-version
```

### Notes

- `--check-version` is optional and will check that the plugin version checked is different from the last committed version in the repository.


## Plugin Builder - `vcv-plugin-builder.py`

Script to support batch build and building individual plugins for (all) supported platforms out of the Rack [library repository](https://github.com/VCVRack/library).

```
python3 ./vcv-plugin-builder.py <RACK_SDK_PATH> <LIBRARY_REPO_ROOT> [--osxcrosslib OSXCROSS_LIB_ROOT] [--clean] [-p SPECIFIC_PLUGIN_TO_BUILD] [--platforms mac linux win]
```

Examples:

- Build **all** plugins for `win` platform only:

```
python3 ./vcv-plugin-builder.py /home/cschol/src/Rack-SDK/Rack-SDK /home/cschol/src/library --osxcrosslib /home/cschol/src/osxcross/target/lib --clean --platforms win
```

- Build individual plugin `modular80` for `mac` and `linux` platform:

```
python3 ./vcv-plugin-builder.py /home/cschol/src/Rack-SDK/Rack-SDK /home/cschol/src/library --osxcrosslib /home/cschol/src/osxcross/target/lib --clean -p modular80 --platforms mac linux
```

### Notes

- `--clean` is optional and will **clean out** the repository before building (using `git clean -dfx`, *here be dragons*!)

### Building the Linux Docker image

Build the `Linux` Docker image with the following command:

```
docker build --build-arg UNAME=${USER} . -t vcvrack/linux-plugin-build
```

See the `build.sh` script in this repository for an example on how to invoke the Docker image to create a build container.

### build.sh script

The `build.sh` script contains an **example** on how to script the build process for all platforms.
It is **my script** that I use for building the plugins during integration. *YMMV*.

### Prerequisites

- `Docker` for Linux build
- `mingw32` toolchain for cross-compilation of Windows binaries on GNU/Linux
- [`osxcross` toolchain](https://github.com/tpoechtrager/osxcross) for cross-compilation of Mac binaires on GNU/Linux
