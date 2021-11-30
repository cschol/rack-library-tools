# VCV Rack Library Tools

Set of tools I use to manage integration of plugins into the VCV Rack `library` repository.

- rack-manifest-validator.py

## General Notes

These tools are specifically written to run on **GNU/Linux**, which is the system I use mostly for integration of plugins in the Plugin Manager.
These tools are written to operate on a local working copy of the Rack [library repository](https://github.com/VCVRack/library).

## Manifest Validator - `rack-manifest-validator.py`

Script to automate batch and individual validation of `plugin.json` manifest(s).

```
python3 ./rack-manifest-validator.py <LIBRARY_REPO_ROOT> [-p SPECIFIC_PLUGIN_TO_VALIDATE]
```

Examples:

- Validate **all** plugin manifests:

```
python3 ./rack-manifest-validator.py /src/library/repos
```

- Validate individual manifest for `modular80`:

```
python3 ./rack-manifest-validator.py /src/library/repos -p modular80
```