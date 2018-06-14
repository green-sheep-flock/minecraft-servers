#!/usr/bin/env python3
from urllib.request import urlopen
from glob import glob
import hashlib
import json
import sys
import os
import re


BUILD_TOOLS_URL = "https://hub.spigotmc.org/jenkins/job/BuildTools/api/json"
ROOT_DIRECTORY = "/opt/minecraft/data/"
BUILD_TOOLS_JAR = "build-tools.jar"
INSTALLED_BUILD_TOOLS_BUILD_NUMBER_FILE = ".build-tools-build-number"
INSTALLED_BUILD_NUMBER_FILE = ".build-number"
BUILD_JAR_NAME = "BuildTools.jar"
SERVER_FILE = "server.jar"


def get_json(url):
    with urlopen(url) as response:
        content = response.read().decode(encoding="UTF-8")
        return json.loads(content)


def md5_hash(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def get_installed_build_tools_build_number():
    installed_build_number = None

    build_number_file = os.path.join(ROOT_DIRECTORY, INSTALLED_BUILD_TOOLS_BUILD_NUMBER_FILE)
    if os.path.isfile(build_number_file):
        with open(build_number_file, "r") as in_file:
            installed_build_number = in_file.read()

    return installed_build_number


def get_installed_build_number():
    installed_build_number = None

    build_number_file = os.path.join(ROOT_DIRECTORY, INSTALLED_BUILD_NUMBER_FILE)
    if os.path.isfile(build_number_file):
        with open(build_number_file, "r") as in_file:
            installed_build_number = in_file.read()

    return installed_build_number


def update_installed_build_tools_build_number(build_number):
    build_number_file = os.path.join(ROOT_DIRECTORY, INSTALLED_BUILD_TOOLS_BUILD_NUMBER_FILE)
    with open(build_number_file, "w") as out_file:
        out_file.write(build_number)


def update_installed_build_number(build_number):
    build_number_file = os.path.join(ROOT_DIRECTORY, INSTALLED_BUILD_NUMBER_FILE)
    with open(build_number_file, "w") as out_file:
        out_file.write(build_number)


def get_spigot_version(file_name):
    match = re.search(".*spigot\\-(.*?)\\.jar", file_name)
    return tuple(int(part) for part in match.group(1).split("."))


def main():
    # Check the latest jenkins build for the Spigot build tools
    builds = get_json(BUILD_TOOLS_URL)
    build_number = str(builds["builds"][0]["number"])

    # Download new build tools if needed
    if build_number != get_installed_build_tools_build_number():
        build = get_json("{}api/json?depth=2".format(builds["builds"][0]["url"]))
        url = "{}artifact/target/BuildTools.jar".format(builds["builds"][0]["url"])

        # Get md5 checksum for build
        checksum = None
        for artifact in build["mavenArtifacts"]["moduleRecords"]:
            if "mainArtifact" in artifact and artifact["mainArtifact"]["fileName"] == BUILD_JAR_NAME:
                checksum = artifact["mainArtifact"]["md5sum"]

        if checksum is None:
            print("Couldn't get md5 checksum for build tools jar!")
            sys.exit(1)

        # Download the build tools jar
        with urlopen(url) as response:
            data = response.read()

        # Verify jar checksum
        md5 = md5_hash(data)
        if checksum != md5:
            print("Downloaded build tools jar ({}) md5 hash ({}) did not match provided checksum ({})!".format(url, md5, checksum))
            sys.exit(1)

        # Write server jar to disk
        with open(os.path.join(ROOT_DIRECTORY, BUILD_TOOLS_JAR), "wb") as out_file:
            out_file.write(data)
        update_installed_build_tools_build_number(build_number)
        print("Downloaded Spigot build tools jar build {}.".format(build_number))

    # Check if we already have the server version built
    version = os.environ.get("SPIGOT_VERSION", "latest").strip().lower()
    build_number = get_json("https://hub.spigotmc.org/versions/{}.json".format(version))["name"]
    if build_number == get_installed_build_number():
        print("Already have Spigot server jar for version: {}".format(version))
        sys.exit(0)

    # Run build tools
    os.chdir(ROOT_DIRECTORY)
    os.system("java -jar {} --rev {}".format(os.path.join(ROOT_DIRECTORY, BUILD_TOOLS_JAR), version))

    # Make symlink to Spigot server jar and update build version
    if version == "latest":
        files = glob(os.path.join(ROOT_DIRECTORY, "spigot-*.jar"))
        if len(files) == 0:
            print("Couldn't find spigot server jar!")
            sys.exit(1)

        versions = [get_spigot_version(file) for file in files]
        versions.sort(reverse=True)
        version = ".".join(str(part) for part in versions[0])

    server = os.path.join(ROOT_DIRECTORY, "spigot-{}.jar".format(version))
    link = os.path.join(ROOT_DIRECTORY, SERVER_FILE)
    if os.path.islink(link):
        os.unlink(link)
    os.symlink(server, link)

    update_installed_build_number(build_number)


if __name__ == "__main__":
    main()
