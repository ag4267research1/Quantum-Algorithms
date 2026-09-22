Quantum-Algorithms
==================

A collection of fundamental quantum algorithms, written to be understood and
compared with their classical counterparts, plus a starting setup for
research-level work on quantum algorithms.

What is here
------------

* **Two tracks.** Python with `Qiskit <https://www.ibm.com/quantum/qiskit>`_
  for circuits, simulators and hardware, and C++ with
  `Armadillo <https://arma.sourceforge.net/>`_ for fast linear algebra.
* **Classical baselines.** Each algorithm is meant to sit next to the best
  simple classical method for the same problem, so the comparison is concrete.
* **Reproducible experiments.** Code is code, experiments are data: every
  run is described by a YAML file rather than numbers edited into source. See
  :doc:`concepts/configuration`.

Getting started
---------------

Setup is a single command on macOS and Linux:

.. code-block:: bash

   ./install.sh
   conda activate qalgos

The pages below cover the details, step by step.

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   setup/python
   setup/conda
   setup/cpp

.. toctree::
   :maxdepth: 1
   :caption: Concepts

   concepts/configuration
