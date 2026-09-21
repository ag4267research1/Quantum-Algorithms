Miniconda tutorial
==================

What conda is
-------------

**Conda** is a package and environment manager. It installs software (Python
libraries, but also compilers and C++ libraries) and keeps different projects
isolated from each other.

**Miniconda** is the minimal installer: conda plus Python, nothing else.
(Anaconda is the same thing with hundreds of packages pre-installed. You do
not need it.)

What an environment is
----------------------

An **environment** is a self-contained folder holding one Python version and
one set of packages. Each project gets its own, so:

* Project A can use Qiskit 2.1 while project B still needs Qiskit 1.x.
* Installing something new can never break another project.
* You can delete an environment and start over without touching your system.

The environment for this repository is called ``qalgos``. It also contains
the C++ compiler, Armadillo and yaml-cpp, so both tracks live in one place.

Everyday commands
-----------------

.. code-block:: bash

   conda env list                     # show all environments (* = active)
   conda create -n myenv python=3.11  # create a new environment
   conda activate qalgos              # enter an environment
   conda deactivate                   # leave it
   conda env remove -n myenv          # delete an environment

Installing packages
-------------------

With the environment **active**:

.. code-block:: bash

   conda install -c conda-forge scipy   # from conda-forge
   pip install qiskit-aer               # from PyPI
   conda list                           # what is installed here

Rule of thumb: try ``conda`` (with the ``conda-forge`` channel) first, then
``pip`` for anything that is not available there. Qiskit itself is installed
with ``pip``. Do not mix the two more than necessary, and always install into
an *active* environment.

Reproducing an environment
--------------------------

The file ``environment.yml`` at the repository root describes the environment.

.. code-block:: bash

   conda env create -f environment.yml          # build it
   conda env update -n qalgos -f environment.yml --prune   # sync after edits
   conda env export --from-history > my_env.yml # save what YOU installed

When you add a dependency, add it to ``environment.yml`` and commit the file.
That is what keeps everyone on the same setup.

Using the environment
---------------------

.. code-block:: bash

   conda activate qalgos
   python run.py configs/example.yaml

In VS Code, pick the interpreter with *Python: Select Interpreter* and choose
``qalgos``. In a script or a scheduler where activation is awkward, use:

.. code-block:: bash

   conda run -n qalgos python run.py configs/example.yaml

Troubleshooting
---------------

``conda: command not found``
   Restart the terminal, or run ``conda init`` for your shell (``zsh``,
   ``bash``) and restart.

Wrong Python after activating
   Run ``which python``. It should point inside ``.../envs/qalgos/``.

Solving the environment is very slow
   Use the ``conda-forge`` channel only and avoid mixing in ``defaults``, as
   ``environment.yml`` already does. Installing ``conda-libmamba-solver`` also
   helps on older conda versions.

Something is broken beyond repair
   Delete and rebuild. That is the point of environments:

   .. code-block:: bash

      conda env remove -n qalgos
      conda env create -f environment.yml
