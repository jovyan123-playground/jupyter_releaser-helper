# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import atexit
import os
import os.path as osp
import re
import shlex
from glob import glob
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen
from tempfile import TemporaryDirectory

from jupyter_releaser import util

PYPROJECT = util.PYPROJECT
SETUP_PY = util.SETUP_PY


def build_dist(dist_dir):
    """Build the python dist files into a dist folder"""
    # Clean the dist folder of existing npm tarballs
    os.makedirs(dist_dir, exist_ok=True)
    dest = Path(dist_dir)
    for pkg in glob(f"{dest}/*.gz") + glob(f"{dest}/*.whl"):
        os.remove(pkg)

    if PYPROJECT.exists():
        util.run(f"python -m build --outdir {dest} .", quiet=True)
    elif SETUP_PY.exists():
        util.run(f"python setup.py sdist --dist-dir {dest}", quiet=True)
        util.run(f"python setup.py bdist_wheel --dist-dir {dest}", quiet=True)


def check_dist(dist_file, test_cmd=""):
    """Check a Python package locally (not as a cli)"""
    dist_file = util.normalize_path(dist_file)
    util.run(f"twine check {dist_file}")

    if not test_cmd:
        # Get the package name from the dist file name
        name = re.match(r"(\S+)-\d", osp.basename(dist_file)).groups()[0]
        name = name.replace("-", "_")
        test_cmd = f'python -c "import {name}"'

    # Create venvs to install dist file
    # run the test command in the venv
    with TemporaryDirectory() as td:
        env_path = util.normalize_path(osp.abspath(td))
        if os.name == "nt":  # pragma: no cover
            bin_path = f"{env_path}/Scripts/"
        else:
            bin_path = f"{env_path}/bin"

        # Create the virtual env, upgrade pip,
        # install, and run test command
        util.run(f"python -m venv {env_path}")
        util.run(f"{bin_path}/python -m pip install -q -U pip")
        util.run(f"{bin_path}/pip install -q {dist_file}")
        util.run(f"{bin_path}/{test_cmd}")


def get_pypi_token(release_url):
    """Get the PyPI token

    Note: Do not print the token in CI since it will not be sanitized
    if it comes from the PYPI_TOKEN_MAP"""
    twine_pwd = os.environ.get("PYPI_TOKEN", "")
    pypi_token_map = os.environ.get("PYPI_TOKEN_MAP", "").replace(r"\n", "\n")
    if pypi_token_map and release_url:
        parts = release_url.replace("https://github.com/", "").split("/")
        repo_name = f"{parts[0]}/{parts[1]}"
        util.log(f"Looking for pypi token for {repo_name} in token map")
        for line in pypi_token_map.splitlines():
            name, _, token = line.partition(",")
            if name == repo_name:
                twine_pwd = token
                util.log("Found pypi token")
    elif twine_pwd:
        util.log(f"Using pypi token from PYPI_TOKEN for {repo_name}")
    else:
        util.log(f"Pypi token not found for {repo_name}")

    return twine_pwd


def start_local_pypi():
    """Start a local PyPI server"""
    temp_dir = TemporaryDirectory()
    cmd = f"pypi-server -p 8081  -P . -a . -o  -v {temp_dir.name}"
    proc = Popen(shlex.split(cmd), stderr=PIPE)
    # Wait for the server to start
    while True:
        line = proc.stderr.readline().decode("utf-8").strip()
        util.log(line)
        if "Listening on" in line:
            break
    atexit.register(proc.kill)
    atexit.register(temp_dir.cleanup)
