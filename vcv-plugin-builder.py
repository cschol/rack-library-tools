import sys
import os
import argparse
import json
import glob
import subprocess
from shutil import which


# Plugins to be excluded from batch build for various reasons.
EXCLUDE_LIST = [
    "Core",
    "VCV-Recorder",
    "Befaco",
    "Fundamental",
    "StellareModular-Link",
    "SurgeRack"
]

SUPPORTED_PLATFORMS = ["win", "mac", "linux"]

MAKE_ENV_LINUX = {"CC": "gcc", "CXX": "g++"}
MAKE_ENV_WIN = {"CC": "x86_64-w64-mingw32-gcc", "CXX": "x86_64-w64-mingw32-g++", "STRIP": "x86_64-w64-mingw32-strip"}
MAKE_ENV_MAC = {"CC": "x86_64-apple-darwin17-clang", "CXX": "x86_64-apple-darwin17-clang++", "STRIP": "x86_64-apple-darwin17-strip"}

PLATFORM_ENVS = {"linux": MAKE_ENV_LINUX, "win": MAKE_ENV_WIN, "mac": MAKE_ENV_MAC}


def parse_args(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("rack_sdk_path", help="Path to Rack SDK", type=str)
    parser.add_argument("root_dir", help="Root directory of library repository", type=str)
    parser.add_argument("-p" , "--plugin", help="Specific plugin to validate", type=str)
    parser.add_argument("--clean" , action='store_true', help="Perform make clean before building", default=False)
    parser.add_argument("--osxcrosslib", help="Lib directory of osxcross", type=str)
    parser.add_argument("--platforms", nargs='+', help="List of specific platforms to build (white-space separated)", type=str)

    return parser.parse_args()


def get_open_source_plugin_list(path):
    plugins = []
    for p in glob.glob(os.path.join(path, "*.json")):
        with open(p, 'r') as m:
            if json.load(m)["license"].lower() == "proprietary": continue
        plugins.append(os.path.basename(p).split(".")[0])
    return sorted(plugins)


def get_source_dir(root_dir, plugin_name):
    return os.path.join(root_dir, "repos", plugin_name)


def build_plugin(source_dir, plugin_name, platform, rack_sdk_path, osxcross_lib_path=None, num_jobs=8, clean=False):
    output = None

    try:
        if clean:
            output = subprocess.check_output(["git", "clean", "-dfx"],
                cwd=source_dir,
                stderr=subprocess.STDOUT)

        # Set up build environment
        build_env = os.environ.copy()
        build_env["RACK_DIR"] = os.path.abspath(rack_sdk_path)
        build_env = {**build_env , **PLATFORM_ENVS[platform]}

        # osxcross needs special handling to ensure proper linking
        if platform == "mac":
            build_env["LD_LIBRARY_PATH"] = os.path.abspath(osxcross_lib_path)

        # Sanity check availability of tool chain
        for tool in PLATFORM_ENVS[platform].keys():
            if which(PLATFORM_ENVS[platform][tool]) is None:
                raise Exception("Toolchain component not found: %s" % PLATFORM_ENVS[platform][tool])

        output = subprocess.check_output(["make", "-j%s" % num_jobs],
            env=build_env,
            cwd=source_dir,
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("FAILED")
        print("\n%s" % e.output.strip().decode("UTF-8") if output else "No output")
        raise e
    except Exception as e:
        print("FAILED")
        raise e


def main(argv=None):

    try:
        args = parse_args(argv)

        if args.plugin:
            plugins = [args.plugin]
        else:
            plugins = get_open_source_plugin_list(os.path.join(args.root_dir, "manifests"))

        filt_plugins = [p for p in plugins if not p in EXCLUDE_LIST]

        failed_plugins = {}

        platforms = []
        if args.platforms:
            for platform in args.platforms:
                if platform in SUPPORTED_PLATFORMS:
                    platforms.append(platform)
                else:
                    raise Exception("Invalid platform: %s" % platform)
        else:
            platforms = SUPPORTED_PLATFORMS

        for platform in platforms:
            for plugin in filt_plugins:
                try:
                    print("[%s] Building plugin on platform %s..." % (plugin, platform), end='', flush=True)
                    source_dir = get_source_dir(args.root_dir, plugin)
                    build_plugin(source_dir, plugin, platform, args.rack_sdk_path, args.osxcrosslib, clean=args.clean)
                    print("OK")
                except subprocess.CalledProcessError as e:
                    failed_plugins[plugin] = " ".join([failed_plugins[plugin], platform]) if plugin in failed_plugins.keys() else platform

        if failed_plugins: print("\n>>> BUILD FAILURES:")
        for f in failed_plugins:
            print("%s %s" % (f, failed_plugins[f]))

        return 1 if failed_plugins else 0

    except Exception as e:
        print("Plugin build FAILED")
        print(e)
        return 1


if __name__ == "__main__":
     sys.exit(main(sys.argv))
