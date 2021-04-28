# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import atexit
import os
from subprocess import Popen
from tempfile import TemporaryDirectory

from jupyter_releaser.util import CHECKOUT_NAME
from jupyter_releaser.util import run

<<<<<<< HEAD
os.environ.setdefault("TWINE_USERNAME", "__token__")
=======
>>>>>>> 88fc657 (wip)
release_url = os.environ["release_url"]
run(f"jupyter-releaser extract-release {release_url}")
run(f"jupyter-releaser forwardport-changelog {release_url}")
run(f"jupyter-releaser publish-release {release_url}")
