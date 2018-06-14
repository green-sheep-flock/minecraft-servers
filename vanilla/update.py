#!/usr/bin/env python3
from urllib.request import urlopen
import hashlib
import json
import sys
import os


VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
ROOT_DIRECTORY = "/opt/minecraft/data/"
SERVER_FILE = "server.jar"
INSTALLED_VERSION_FILE = ".version"


def get_json(url):
    with urlopen(url) as response:
        content = response.read().decode(encoding="UTF-8")
        return json.loads(content)


def sha1_hash(data):
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.hexdigest()


def get_installed_version():
    installed_version = None

    version_file = os.path.join(ROOT_DIRECTORY, INSTALLED_VERSION_FILE)
    if os.path.isfile(version_file):
        with open(version_file, "r") as in_file:
            installed_version = in_file.read()

    return installed_version


def update_installed_version(version):
    version_file = os.path.join(ROOT_DIRECTORY, INSTALLED_VERSION_FILE)
    with open(version_file, "w") as out_file:
        out_file.write(version)


def main():
    # Determine which version is desired
    # Uses MINECRAFT_VERSION environment variable
    # Special values "release" and "snapshot" will get the latest version
    # The default is "release"
    version = os.environ.get("MINECRAFT_VERSION", "release").strip().lower()
    if version == "release" or version == "snapshot":
        versions = get_json(VERSION_MANIFEST_URL)
        version = versions["latest"][version]

    # Check if we already have the server jar for that version
    if version == get_installed_version():
        print("Already have server jar version {}.".format(version))
        sys.exit(0)

    # Get version manifest url
    try:
        versions
    except NameError:
        versions = get_json(VERSION_MANIFEST_URL)

    url = None
    for version_info in versions["versions"]:
        if version == version_info["id"]:
            url = version_info["url"]
            break

    if url is None:
        print("Resolved version number could not be found: {}".format(version))
        sys.exit(1)

    # Get server jar download url
    manifest = get_json(url)
    url = manifest["downloads"]["server"]["url"]
    checksum = manifest["downloads"]["server"]["sha1"]

    # Download the server jar
    with urlopen(url) as response:
        data = response.read()

    # Verify jar checksum
    sha1 = sha1_hash(data)
    if checksum != sha1:
        print("Downloaded server jar ({}) sha1 hash ({}) did not match provided checksum ({})!".format(url, sha1, checksum))
        sys.exit(1)

    # Write server jar to disk
    with open(os.path.join(ROOT_DIRECTORY, SERVER_FILE), "wb") as out_file:
        out_file.write(data)
    update_installed_version(version)
    print("Downloaded server jar version {}.".format(version))


if __name__ == "__main__":
    main()
