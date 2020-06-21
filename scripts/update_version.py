"""
Automate the generation of release candidate versions
for rc/ named branches.
"""
import subprocess
import sys
from typing import Optional, Tuple

VERSION_FILE = "VERSION"


def main():
    branch = get_current_branch()
    if branch != "master" and not branch.startswith("rc/"):
        print(f"not a valid branch for uploading version: '{branch}'")
        return

    if branch.startswith("rc/"):
        update_rc_version()


def get_current_branch() -> str:
    p = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
    if p.returncode != 0:
        raise SystemExit("Unable to determine current git branch name")
    return p.stdout.decode("utf-8").strip()


def update_rc_version():
    # Extract the first 8 chars of the git hash and create a new rc version
    version = get_version()
    last_rc = get_last_rc_version(version)
    update_version_file(version, last_rc + 1)


def get_last_rc_version(this_version: str) -> int:
    p = subprocess.run(["pip", "search", "jsonmarshal"], capture_output=True)
    if p.returncode != 0:
        raise SystemExit("Unable to determine current git branch name")

    # A list to contain the existing rc versions deployed
    cur_rcs = []

    resp = p.stdout.decode("utf-8").strip()
    for line in resp.split("\n"):
        elems = line.split()
        if elems[0] != "jsonmarshal":
            continue
        version = elems[1].strip("()")

        major, minor, patch, rc = split_ver(version)

        if f"{major}.{minor}.{patch}" != this_version:
            continue
        cur_rcs.append(rc)
    if not cur_rcs:
        return 0
    return max(cur_rcs)


def split_ver(version: str) -> Tuple[int, int, int, int]:
    major, minor, patch = version.split(".")
    if "rc" in patch:
        patch, rc = patch.split("rc")
    else:
        rc = 0
    return int(major), int(minor), int(patch), int(rc)


def get_version() -> str:
    with open(VERSION_FILE, "r") as buf:
        v = buf.read()

    # version is symantic.  Need 3 parts and last part must be an integer
    # otherwise we cant update the version.
    parts = v.split(".")
    if len(parts) != 3 or not parts[2].isnumeric():
        raise SystemExit(f"version is invalid: '{v}'")
    return v


def update_version_file(version: str, rc_ver: int):
    with open(VERSION_FILE, "w") as buf:
        buf.write(f"{version}rc{rc_ver}")


if __name__ == "__main__":
    sys.exit(main())
