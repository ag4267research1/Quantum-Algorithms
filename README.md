# Quantum-Algorithms

This repository contains a collection of fundamental algorithms to understand quantum computing and compare it with classical computation also. It also gives the necessary tools needed to have a basic setup at research level for quantum algorithms.

There are two tracks: **Python** (Qiskit) and **C++** (Qiskit C++ for circuits, Armadillo for linear algebra).

Documentation: http://theory-code.com/Quantum-Algorithms/

## Quick start

On macOS or Linux (on Windows, use WSL2):

```bash
./install.sh                # Miniconda (if missing) + the `qalgos` environment
conda activate qalgos
```

For the C++ track, also build Qiskit C++ (first build takes several minutes):

```bash
./scripts/install_qiskit_cpp.sh
```

To run on real IBM hardware you need a free IBM Quantum Open Plan account. See the
[IBM setup guide](http://theory-code.com/Quantum-Algorithms/ibm_setup/open_plan.html).
The IBM setup covers the Python track only for now; C++ hardware access is not set up yet.
After saving your credentials, `python ibm_check/check_ibm.py` tells you whether everything works
and lists the QPUs you can use. Simulators need no account.

## Repository structure

```text
Quantum-Algorithms/
├── README.md
├── install.sh                 # one-shot setup: Miniconda + qalgos environment
├── environment.yml            # conda environment (Python, Qiskit, C++ toolchain, Armadillo)
├── scripts/
│   └── install_qiskit_cpp.sh  # builds the Qiskit C library, fetches Qiskit C++ headers
├── ibm_check/
│   ├── check_ibm.py           # checks your setup and lists the available IBM QPUs
│   └── README.md
├── docs/                      # Sphinx documentation (published to GitHub Pages)
│   ├── index.rst              # landing page
│   ├── conf.py
│   ├── requirements.txt       # docs build only; users do not need Sphinx
│   ├── _static/
│   │   └── custom.css
│   ├── setup/
│   │   ├── python.rst         # Python and Qiskit setup
│   │   ├── conda.rst          # Miniconda tutorial
│   │   └── cpp.rst            # Qiskit C++ and Armadillo setup
│   ├── ibm_setup/
│   │   ├── open_plan.rst      # IBM Quantum account and Open Plan
│   │   └── credentials.rst    # API key, saving credentials, first connection
│   └── concepts/
│       └── configuration.rst  # keeping experiments in YAML, not in code
├── .github/
│   └── workflows/
│       └── docs.yml           # builds and deploys the docs to GitHub Pages
└── .readthedocs.yaml
```

Created locally and not committed: `third_party/` (Qiskit and Qiskit C++ sources) and `build/`.
