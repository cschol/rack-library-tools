# VCV Library Tools

Set of tools I use to manage integration of plugins into the VCV Rack `library` repository.

- vcv-manifest-validator.py

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
