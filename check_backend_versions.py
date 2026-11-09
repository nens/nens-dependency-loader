"""Check that the threedi-schema pin in dependencies.py matches the backend.

 Requires the HCC_API_TOKEN environment variable (Personal API key).
"""
import base64
import json
import os
import sys
import urllib.request

from packaging.version import Version

URL = "https://hcc-api.ranawaterintelligence.com/v3/package-versions/"
PACKAGE = "threedi-schema"


def local_version():
    # dependencies.py imports qgis, so this must run where QGIS is installed.
    from dependencies import DEPENDENCIES

    for dependency in DEPENDENCIES:
        if dependency.name == PACKAGE:
            if not dependency.constraint.startswith("=="):
                raise ValueError(f"{PACKAGE} is not pinned with ==")
            return dependency.constraint[2:]
    raise ValueError(f"Could not find {PACKAGE} in dependencies.py")


def backend_version():
    token = os.environ.get("HCC_API_TOKEN")
    if not token:
        raise ValueError("HCC_API_TOKEN is not set")
    request = urllib.request.Request(
        URL,
        headers={
            "Authorization": "Basic "
            + base64.b64encode(f"__key__:{token}".encode()).decode("ascii"),
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    return data.get(PACKAGE)


def main():
    try:
        local, backend = local_version(), backend_version()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if backend is None:
        print(f"Error: {PACKAGE} not found in backend response", file=sys.stderr)
        return 2
    if Version(local) > Version(backend):
        print(
            f"{PACKAGE} is newer locally: dependencies.py has {local}, backend has {backend}",
            file=sys.stderr,
        )
        return 1
    print(f"{PACKAGE} versions match: {local} <= {backend}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
