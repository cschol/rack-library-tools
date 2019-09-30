import sys
import os
import argparse
import json
import traceback
import glob
import subprocess
import requests


URL_KEYS = ["pluginUrl", "authorUrl", "manualUrl", "sourceUrl", "changelogUrl"]
SPDX_URL = "https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"
RACK_TAG_CPP_URL = "https://raw.githubusercontent.com/VCVRack/Rack/v1/src/tag.cpp"


REQUIRED_TOP_LEVEL_KEYS = [
    "slug",
    "name",
    "version",
    "license",
    "author",
    "brand",
    "authorEmail",
    "authorUrl",
    "pluginUrl",
    "manualUrl",
    "sourceUrl",
    "modules"
]


REQUIRED_MODULE_KEYS = [
    "slug",
    "name",
    "description",
    "tags"
]


def parse_args(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("plugin_root" , help="Root directory of plugins, e.g. library repo root", type=str)
    parser.add_argument("-p" , "--plugin", help="Specific plugin to validate", type=str)
    parser.add_argument("--slugsfile", help="File containing known module slugs", type=str)
    parser.add_argument("--check-version", help="Check plugin version against last known version in repository", action='store_true')

    return parser.parse_args()


def get_submodule_sha(plugin_root, plugin_path):
    try:
        output = subprocess.check_output(["git", "ls-files", "-s", plugin_path],
            cwd=plugin_root,
            stderr=subprocess.STDOUT)
        return output.strip().decode("UTF-8").split(" ")[1]
    except Exception:
        return None


def get_plugin_head_sha(plugin_path):
    try:
        output = subprocess.check_output(["git", "rev-parse", "HEAD"],
            cwd=plugin_path,
            stderr=subprocess.STDOUT)
        return output.strip().decode("UTF-8")
    except Exception:
        return None


def get_plugin_version(plugin_path, sha):
    try:
        output = subprocess.check_output(["git", "show", "%s:plugin.json" % sha],
            cwd=plugin_path,
            stderr=subprocess.STDOUT)
        pj = json.loads(output.strip().decode("UTF-8"))
        return pj["version"]
    except Exception:
        raise


def get_valid_tags():
    tag_cpp = requests.get(RACK_TAG_CPP_URL).text
    tags = []
    capture_tags = False
    for line in tag_cpp.split("\n"):
        if "tagAliases" in line.strip():
            capture_tags = True
            continue
        if capture_tags and line.strip() == "};":
            capture_tags = False
            break
        if capture_tags:
            for t in line.strip().split("}")[0].split(","):
                tags.append(t.strip().replace('{','').replace('"','').lower())
    return tags


def get_spdx_license_ids():
    import requests
    license_json = json.loads(
        requests.get(SPDX_URL).text
        )
    return [license["licenseId"] for license in license_json["licenses"]]


def validate_tags(tags, valid_tags):
    invalid_tags = []
    for tag in tags:
        if tag.lower() not in valid_tags:
            invalid_tags.append(tag)
    return invalid_tags if invalid_tags else None


def validate_url(url):
    import httplib2
    import urllib.parse

    try:
        p = urllib.parse.urlparse(url)
        conn = httplib2.HTTPConnectionWithTimeout(p.netloc)
        conn.request('HEAD', p.path)
        resp = conn.getresponse()
        return resp.status >= 400
    except Exception:
        return 1


def validate_slug(slug):
    for c in slug:
        if not (c.isalnum() or c == '-' or c == '_'):
            return 1
    return 0


def read_slugs_file(db_file):
    content = None
    with open(db_file, 'r') as f:
        content = f.readlines()
    return content


def find_slug(slug, known_slugs):
    looking_for_slug = True
    for line in known_slugs:
        if slug in line:
            looking_for_slug = False
            break
    return looking_for_slug


def main(argv=None):

    args = parse_args(argv)
    plugin_root = args.plugin_root
    slugs_file = args.slugsfile

    try:

        failed = False
        known_slugs = None

        if not os.path.exists(plugin_root):
            raise Exception("Invalid Plugin root: %s" % plugin_root)

        # Adjust plugin_root if we are in the library repository.
        repos_path = os.path.join(plugin_root, "repos")
        if os.path.exists(repos_path):
            plugin_root = repos_path

        if args.slugsfile:
            if not os.path.exists(args.slugsfile):
                raise Exception("Invalid slugs file: %s" % slugs_file)
            else:
                known_slugs = read_slugs_file(slugs_file)

        if args.plugin:
            plugins = [os.path.join(plugin_root, args.plugin)]
        else:
            plugins = glob.glob(plugin_root+"/*")

        for plugin_path in sorted(plugins):
            try:
                plugin_json = None
                failed = False
                output = []

                if not os.path.exists(plugin_path):
                    raise Exception("Invalid plugin path: %s" % plugin_path)

                manifest = os.path.join(plugin_path, "plugin.json")
                with open(manifest, 'r') as p:
                    plugin_json = json.load(p)

                valid_tags = get_valid_tags()
                valid_license_ids = get_spdx_license_ids()

                # Validate top-level manifest keys
                for key in REQUIRED_TOP_LEVEL_KEYS:
                    if key not in plugin_json.keys():
                        output.append("Missing key: %s" % key)
                        failed = True

                # Validate plugin slug
                if validate_slug(plugin_json["slug"]):
                    output.append("%s: invalid plugin slug" % (plugin_json["slug"]))
                    failed = True

                # Check if plugin slug has changed compared to last known 0.6 version
                if args.slugsfile:
                    if find_slug(plugin_json["slug"], known_slugs):
                        output.append("%s: plugin slug flagged" % plugin_json["slug"])
                        failed = True

                # Validate module entries
                modules = plugin_json["modules"]

                invalid_tag = False
                invalid_slug = False
                for module in modules:
                    for key in REQUIRED_MODULE_KEYS:
                        if key not in module.keys():
                            output.append("%s: missing key: %s" % (module["slug"], key))
                            if key == "pluginUrl":
                                output.append("-- Please set `pluginUrl` to README.md of the plugin Github repo")
                            if key == "sourceUrl":
                                output.append("-- Please set `sourceUrl` to the plugin Github repo")
                            failed = True

                    # Validate tags
                    if "tags" in module.keys():
                        res = validate_tags(module["tags"], valid_tags)
                        if res:
                            output.append("%s: invalid module tags: %s" % (module["slug"], ", ".join(res)))
                            invalid_tag = True

                    # Validate slugs
                    if "slug" in module.keys():
                        if validate_slug(module["slug"]):
                            output.append("%s: invalid module slug" % (module["slug"]))
                            invalid_slug = True

                        # Check if module slug has changed compared to last known 0.6 version
                        if args.slugsfile:
                            if find_slug(module["slug"], known_slugs):
                                output.append("%s: module slug flagged" % module["slug"])
                                failed = True

                if invalid_tag:
                    output.append("-- Valid tags are defined in https://github.com/VCVRack/Rack/blob/v1/src/tag.cpp")
                    failed = True

                if invalid_slug:
                    output.append("-- Valid slugs are defined in https://vcvrack.com/manual/PluginDevelopmentTutorial.html#naming")
                    failed = True

                # Validate URLs
                for key in URL_KEYS:
                    if key in plugin_json.keys():
                        if not plugin_json[key]:
                            output.append("%s: no URL specified" % key)
                            failed = True
                            continue
                        if validate_url(plugin_json[key]):
                            output.append("Invalid URL: %s" % plugin_json[key])
                            failed = True

                # Validate license is a valid SPDX ID
                if plugin_json["license"] not in valid_license_ids:
                    output.append("Invalid license ID: %s" % plugin_json["license"])
                    output.append("-- License must be a valid Identifier from https://spdx.org/licenses/")
                    failed = True

                # Validate that plugin version has been updated.
                # Only applies if the repository is a submodule with a previously recorded SHA.
                if os.path.exists(os.path.join(plugin_root, ".gitmodules")):
                    submodule_sha = get_submodule_sha(plugin_root, plugin_path)
                    # If this is a new plugin or a newly migrated plugin, plugin.json does not exist in an old version
                    if submodule_sha:
                        head_sha = get_plugin_head_sha(plugin_path)
                        old_version = get_plugin_version(plugin_path, submodule_sha)
                        new_version = get_plugin_version(plugin_path, head_sha)
                        if old_version == new_version:
                            output.append("Version needs update! Current version: %s" % old_version)
                            failed = True

            except FileNotFoundError as e:
                # No plugin.json to validate. Ignore.
                pass
            except json.decoder.JSONDecodeError as e:
                output.append("Invalid JSON format: %s" % e)
                failed = True
            except Exception as e:
                output.append("ERROR: %s" % e)
                failed = True

            plugin_name = os.path.basename(os.path.abspath(plugin_path)) # from path
            if failed:
                print("[%s] Issues found in `plugin.json`:\n" % plugin_name)
                print("\n".join(output))
                print()
            else:
                print("[%s] Manifest validation...OK" % plugin_name)

        return 1 if failed else 0

    except Exception as e:
        print("ERROR: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
