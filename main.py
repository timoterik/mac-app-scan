#  Copyright © 2022 - 2023, DCCTech. All Rights Reserved.
#  This copyright notice is the exclusive property of DCCTech and is hereby granted to users
#  for use of DCCTech's intellectual property.
#  Any reproduction, modification, distribution, or other use of DCCTech's intellectual property without prior written
#  consent is strictly prohibited.

import random
import string
import subprocess

import requests


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
    headers = {
               'Accept': '*/*', 'Content-Type': 'application/json',
               'Cookie': f'mpv={generate_cookie(72)}; muid={generate_cookie(8)}-{generate_cookie()}-{generate_cookie()}-{generate_cookie()}-{generate_cookie(12)}',
               # 'host': 'api.macupdate.com', 'Origin': 'https://www.macupdate.com',
               # 'Referer': 'https://www.macupdate.com/',
               'X-ClientId': 'vijgyb6v1gjc7m6l',
               }
    url = f"https://api.macupdate.com/v1/apps/search/list/10/0?context={app_name}"
    response = requests.get(url, headers=headers)
    version = None
    if response.status_code == 200:
        response_dict = response.json()
        if response_dict["data"] is not None:
            for app in response_dict["data"]:
                if "apple" in (f"{app['title']}".lower() or f"{app['title_slug']}".lower() or f"{app['download_url'].get('url')}".lower() or
                               f"{app['download_url'].get('type')}".lower() or f"{app['short_description']}".lower() ):
                    return app["version"]

            return response.json()["data"][0]["version"]
    else:
        return version


def compare_versions():
    local_versions = get_local_versions()
    for app, local_version in local_versions.items():
        web_version = get_web_version(app)
        print(
            f"{app}: Local Version - {local_version if local_version != (None or '(null)') else 'unknown'}, latest "
            f"version - {web_version if web_version is not None else 'unknown'}")
        if web_version is None:
            print("\t cannot find the current version of the application on the Internet.")
        elif local_version == web_version:
            print(f"{app} is up to date.")
        elif local_version < web_version:
            print("\t has a newer version available.")
        elif local_version > web_version:
            print("\t cannot find the current version of the application on the Internet.")
        else:
            print("\t Version not found.")


def generate_cookie(length=4):
    """Generate a random cookie string of the specified length."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    cookie = ''.join(random.choice(characters) for _ in range(length))
    return cookie


if __name__ == '__main__':
    compare_versions()
