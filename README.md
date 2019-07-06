# vcv-library-tools

Set of tools to manage VCV Rack `library` repository content.

## General Notes

These tools are specifically written to run on **GNU/Linux**, which is the system I use mostly for integration of plugins in the Plugin Manager.

## Manifest Validator

Script to automate validation of `plugin.json` manifest.

```
python3 ./vcv-manifest-validator.py <RACK_SOURCE_DIR> <LIBRARY_REPO_ROOT> [-p SPECIFIC_PLUGIN_TO_VALIDATE] [--check-version]
```

Example:

```
python3 ./vcv-manifest-validator.py /home/cschol/src/Rack-1.0 /home/cschol/src/library/repos -p modular80 --check-version
```

## Plugin Builder

```
python3 ./vcv-plugin-builder.py <RACK_SDK_PATH> <LIBRARY_REPO_ROOT> [--osxcrosslib OSXCROSS_LIB_ROOT] [--clean] [-p SPECIFIC_PLUGIN_TO_BUILD]
```

Example:

```
python3 ./vcv-plugin-builder.py /home/cschol/src/Rack-SDK/Rack-SDK /home/cschol/src/library --osxcrosslib /home/cschol/src/osxcross/target/lib --clean -p modular80
```

### Prerequisites

- `mingw32` toolchain for cross-compilation of Windows binaries on GNU/Linux
- [`osxcross` toolchain](https://github.com/tpoechtrager/osxcross) for cross-compilation of Mac binaires on GNU/Linux
