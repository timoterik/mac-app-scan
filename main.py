
#  Copyright © 2022 - 2023, DCCTech. All Rights Reserved.
#  This copyright notice is the exclusive property of DCCTech and is hereby granted to users
#  for use of DCCTech's intellectual property.
#  Any reproduction, modification, distribution, or other use of DCCTech's intellectual property without prior written
#  consent is strictly prohibited.

import subprocess

import requests
from bs4 import BeautifulSoup


def get_local_versions():
    command = "mdfind \"kMDItemContentTypeTree == 'com.apple.application' && kMDItemKind != 'Folder'\""
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    lines = output.strip().split("\n")
    versions = {}
    for line in lines:
        parts = line.split("/")
        app = parts[-1].replace(".app", "")
        version_str = subprocess.check_output(["mdls", "-name", "kMDItemVersion", line]).decode("utf-8")
        version = version_str.split('=')[1].strip().strip('"')
        versions[app] = version
    return versions


def get_web_version(app_name):
    url = f"https://www.macupdate.com/find/mac/{app_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    version_element = soup.find("div", class_="version")
    if version_element:
        return version_element.text.strip()
    else:
        return "Version not found"


def compare_versions():
    local_versions = get_local_versions()
    for app, local_version in local_versions.items():
        web_version = get_web_version(app)
        print(f"{app}: Local Version - {local_version if local_version is not None else 'unknown'}, latest version - {web_version}")
        if local_version == web_version:
            print(f"{app} is up to date.")
        elif web_version != "Version not found":
            print("\t has a newer version available.")
        elif local_versions:
            print("\t cannot find an online version.")
        else:
            print("\t Version not found")


if __name__ == '__main__':
    compare_versions()
