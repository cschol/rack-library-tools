import sys
import os
import argparse
import json
import glob
import subprocess
import traceback


# Plugins to be excluded from batch build for various reasons.
EXCLUDE_LIST = [
    "Core",
    "VCV-Recorder",
    "Befaco",
    "Fundamental",
    "StellareModular-Link"
]

SUPPORTED_PLATFORMS = ["win", "mac", "linux"]

def parse_args(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("root_dir", help="Root directory containing one (or more) plugins", type=str)
    parser.add_argument("-p" , "--plugin", help="Name of plugin to build", type=str)
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
    # If 'repos' directory exists in root_dir we assume we are in a 'library' repo checkout.
    if os.path.exists(os.path.join(root_dir, "repos")):
        return os.path.join(root_dir, "repos", plugin_name)
    else: # just use the root_dir as a folder containing the plugin subfolder.
        return os.path.join(root_dir, plugin_name)


def run(cmd, dir, build_env):
    return subprocess.check_output(cmd.split(" "),
        env=build_env,
        cwd=dir)


def update_source(source_dir):
    output = None

    try:
        update_cmd = "git submodule update --init --recursive"
        output = run(update_cmd, source_dir, {})
        return output
    except subprocess.CalledProcessError as e:
        print("FAILED")
        print("\n%s" % e.output.strip().decode("UTF-8") if output else "No output")
        raise e
    except Exception as e:
        print("FAILED")
        raise e


def build_plugin(source_dir, plugin_name, platform, num_jobs=8):
    output = bytes()

    try:
        # Set up build environment
        build_env = os.environ.copy()

        # Clean repository before building
        output += subprocess.check_output(["git", "clean", "-dfx"],
            cwd=source_dir,
            stderr=subprocess.STDOUT)

        make_cmd = "make -j%s" % num_jobs
        output += run("%s clean" % make_cmd, source_dir, build_env)
        output += run("%s cleandep" % make_cmd, source_dir, build_env)
        # Ensure that all submodules are present
        output += update_source(source_dir)

        output += run("%s dep" % make_cmd, source_dir, build_env)
        output += run("%s dist" % make_cmd, source_dir, build_env)

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
            filt_plugins = plugins
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
                    source_dir = get_source_dir(args.root_dir, plugin)
                    print("[%s] Building plugin on platform %s..." % (plugin, platform), end='', flush=True)
                    build_plugin(source_dir, plugin, platform)
                    print("OK")
                except subprocess.CalledProcessError:
                    failed_plugins[plugin] = " ".join([failed_plugins[plugin], platform]) if plugin in failed_plugins.keys() else platform

        if failed_plugins: print("\n>>> BUILD FAILURES:")
        for f in failed_plugins:
            print("%s %s" % (f, failed_plugins[f]))

        return 1 if failed_plugins else 0

    except Exception:
        print("Plugin build FAILED")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
     sys.exit(main(sys.argv))
