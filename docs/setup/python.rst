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

Run this single block. It does nothing if conda is already there, and it
picks the right installer for your machine (``uname -m`` reports ``arm64`` for
Apple silicon and ``x86_64`` for Intel), so you never choose one by hand:

.. code-block:: bash

   if command -v conda >/dev/null 2>&1 || [ -x "$HOME/miniconda3/bin/conda" ]; then
     echo "conda is already installed, skip to step 2"
   else
     case "$(uname -s)-$(uname -m)" in
       Darwin-arm64)  f=Miniconda3-latest-MacOSX-arm64.sh ;;
       Darwin-x86_64) f=Miniconda3-latest-MacOSX-x86_64.sh ;;
       Linux-x86_64)  f=Miniconda3-latest-Linux-x86_64.sh ;;
       Linux-aarch64) f=Miniconda3-latest-Linux-aarch64.sh ;;
       *) echo "Unsupported platform (on Windows, use WSL2)"; f= ;;
     esac
     [ -n "$f" ] && curl -fsSLO "https://repo.anaconda.com/miniconda/$f" && bash "$f"
   fi

.. warning::

   Do not run the Miniconda installer by hand if conda already works. If the
   folder ``~/miniconda3`` exists, the installer stops with *File or
   directory already exists*. That is harmless, and it means you already have
   conda: go to step 2.

   Do not install the wrong architecture either. An x86_64 Miniconda on an
   Apple silicon Mac runs under Rosetta and is noticeably slower.

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
