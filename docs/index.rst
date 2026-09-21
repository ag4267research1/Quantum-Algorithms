Quantum-Algorithms
==================

A Qiskit-focused collection of fundamental quantum algorithms, with classical
baselines for comparison and a starting setup for research-level work. There
are two tracks: **Python** (Qiskit) and **C++** (Armadillo).

.. toctree::
   :maxdepth: 2
   :caption: Setup

   setup/python
   setup/conda
   setup/cpp

Why separate code from inputs
-----------------------------

The one rule this repository follows everywhere: **code is code,
experiments are data.** The program says *how* to do something. A YAML file
says *which* instance to run: how many qubits, how many shots, which backend,
which noise model, which random seed.

The anti-pattern
~~~~~~~~~~~~~~~~

.. code-block:: python

   # run.py: every number is hard-coded
   n_qubits = 4
   shots = 4096
   seed = 7
   backend = "aer_simulator"

To try 5 qubits you edit the source. To compare three noise levels you copy
the file three times. Six months later, nobody remembers which edited copy
produced Figure 3.

The pattern
~~~~~~~~~~~

The inputs live in a YAML file:

.. code-block:: yaml

   # configs/example.yaml
   n_qubits: 4
   shots: 4096
   seed: 7
   backend:
     name: aer_simulator
     noise: null

and the program only reads and validates them:

.. code-block:: python

   # run.py
   import sys
   import yaml
   from pydantic import BaseModel


   class Config(BaseModel):
       n_qubits: int
       shots: int = 1024
       seed: int = 0


   with open(sys.argv[1]) as f:
       cfg = Config(**yaml.safe_load(f))

.. code-block:: bash

   python run.py configs/example.yaml
   python run.py configs/example_5q.yaml

What you gain
~~~~~~~~~~~~~

* **Reproducibility.** A result is (code version, config file). Commit the
  config and anyone can regenerate the figure exactly.
* **Sweeps without edits.** A parameter study is a folder of YAML files or a
  short loop, and the program never changes.
* **Validation.** The schema rejects ``n_qubits: -3`` before a long job
  starts, with a clear message.
* **One config, two languages.** The same YAML file can be read by the Python
  and the C++ track, so the two can be compared on identical inputs.
* **Collaboration.** A collaborator who does not read your code can still
  change and run an experiment.

Reading the same file in C++
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

   // main.cpp
   #include <yaml-cpp/yaml.h>

   int main(int argc, char** argv) {
       YAML::Node cfg = YAML::LoadFile(argv[1]);
       const int n_qubits = cfg["n_qubits"].as<int>();
       const int shots = cfg["shots"].as<int>(1024);
       return 0;
   }

Rules of thumb
~~~~~~~~~~~~~~

* Put **every number that defines an experiment** in YAML: sizes, seeds,
  shots, tolerances, backend names, noise parameters, file paths.
* Keep **secrets** (IBM Quantum API tokens) out of YAML that gets committed.
  Use environment variables.
* Load with ``yaml.safe_load``, never ``yaml.load``.
* Validate on load, and fail early.
* Save the config alongside the results it produced.
