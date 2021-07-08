# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from jupyter_releaser.util import run

run("jupyter-releaser prep-git")
run("ls .jupyter_releaser_checkout")
run("cat .jupyter_releaser_checkout/pyproject.toml")
raise ValueError("wat")
run("jupyter-releaser bump-version")
run("jupyter-releaser build-changelog")
run("jupyter-releaser draft-changelog")
