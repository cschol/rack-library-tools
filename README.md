# VCV Library Tools

Set of tools to manage integration of plugins into the VCV Rack `library` repository.

- vcv-manifest-validator.py
- vcv-plugin-builder.py

## General Notes

These tools are specifically written to run on **GNU/Linux**, which is the system I use mostly for integration of plugins in the Plugin Manager.
These tools are written to operate on a local working copy of the Rack [library repository](https://github.com/VCVRack/library).

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


### Prerequisites

- `mingw32` toolchain for cross-compilation of Windows binaries on GNU/Linux
- [`osxcross` toolchain](https://github.com/tpoechtrager/osxcross) for cross-compilation of Mac binaires on GNU/Linux
