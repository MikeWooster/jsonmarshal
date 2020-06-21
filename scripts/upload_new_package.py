"""
PyPi package uploader that doesn't return a bad status code
if the package already exists.
"""
import subprocess
import sys

from requests import HTTPError
from twine.cli import dispatch

VERSION_FILE = "VERSION"


def main():
    branch = get_current_branch()
    if branch != "master" and not branch.startswith("rc/"):
        print(f"not a valid branch for uploading version: '{branch}'")
        return
    upload_to_pypi()


def get_current_branch() -> str:
    p = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
    if p.returncode == 0:
        return p.stdout.decode("utf-8").strip()
    raise SystemExit("Unable to determine current git branch name")


def upload_to_pypi():
    try:
        return dispatch(["upload", "dist/*"])
    except HTTPError as error:
        handle_http_error(error)


def handle_http_error(error: HTTPError):
    try:
        if error.response.status_code == 400:
            print(error)
        else:
            raise error
    except Exception:
        raise error


if __name__ == "__main__":
    sys.exit(main())
