Python setup (Qiskit)
=====================

The Python track uses Qiskit inside a Miniconda environment. New to conda?
Read :doc:`conda` first.

Fast path
---------

From the repository root, on macOS (Apple silicon or Intel) or Linux:

.. code-block:: bash

   ./install.sh
   conda activate qalgos

The script uses your existing conda if you have one (Miniconda, Anaconda or
Miniforge, on the PATH or in the usual folders) and installs Miniconda only if
none is found. It then creates the ``qalgos``
environment from ``environment.yml``, and checks that everything imports. On
Windows, use WSL2 and run the same script inside it.

Manual path
-----------

1. Install Miniconda (only if you do not have conda)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First check whether conda is already installed:

.. code-block:: bash

   conda --version

If this prints a version (for example ``conda 24.9.2``), you already have
conda. **Skip the rest of this step** and go to step 2. Do not install a
second copy. This also applies to Anaconda and Miniforge.

If you get ``command not found``, conda may still be installed but not set up
in your shell. Look for it before installing anything:

.. code-block:: bash

   ls -d ~/miniconda3 ~/anaconda3 ~/miniforge3 2>/dev/null

If one of those exists, run ``~/miniconda3/bin/conda init`` (use the folder
you found), restart the terminal, and check ``conda --version`` again. Only if
nothing is found, install Miniconda as follows.

Pick the installer that matches your machine. If you are not sure which Mac
you have, run ``uname -m``: ``arm64`` means Apple silicon (M1/M2/M3/M4),
``x86_64`` means Intel.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Platform
     - Installer
   * - macOS, Apple silicon (arm64)
     - ``Miniconda3-latest-MacOSX-arm64.sh``
   * - macOS, Intel (x86_64)
     - ``Miniconda3-latest-MacOSX-x86_64.sh``
   * - Linux, x86_64
     - ``Miniconda3-latest-Linux-x86_64.sh``
   * - Linux, aarch64
     - ``Miniconda3-latest-Linux-aarch64.sh``
   * - Windows
     - Use WSL2 and follow the Linux steps

.. code-block:: bash

   # macOS, Apple silicon
   curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
   bash Miniconda3-latest-MacOSX-arm64.sh

   # macOS, Intel
   curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
   bash Miniconda3-latest-MacOSX-x86_64.sh

   # Linux, x86_64
   curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh

Do not install the wrong architecture. An x86_64 Miniconda on an Apple
silicon Mac runs under Rosetta and is noticeably slower. ``install.sh`` picks
the right one automatically.

Restart the terminal, then check:

.. code-block:: bash

   conda --version

2. Create the environment
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   conda env create -f environment.yml
   conda activate qalgos

3. Verify
~~~~~~~~~

.. code-block:: bash

   python -c "import qiskit, qiskit_aer, yaml; print(qiskit.__version__)"

What gets installed
-------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Package
     - Purpose
   * - ``qiskit``
     - Circuits, transpiler, primitives, ``quantum_info``
   * - ``qiskit-aer``
     - Fast simulators and noise models
   * - ``qiskit-ibm-runtime``
     - Real IBM hardware and fake backends
   * - ``numpy``, ``scipy``
     - Numerics, optimizers, sparse linear algebra
   * - ``pyyaml``, ``pydantic``
     - Reading and validating YAML inputs
   * - ``matplotlib``, ``pylatexenc``
     - Plots and circuit drawings
   * - ``pandas``, ``tqdm``, ``sympy``, ``networkx``
     - Results, progress bars, symbolic checks, graph problems
   * - ``pytest``, ``ruff``
     - Tests and linting

Optional add-ons such as ``qiskit-nature`` and ``qiskit-optimization`` are not
installed by default. Add them to ``environment.yml`` if you need chemistry or
QUBO problems, and check that the release supports your Qiskit version.
