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
After saving your credentials, this tells you whether everything works and lists the QPUs you can use:

```bash
python ibm_check/check_ibm.py
# or, without cloning the repository (environment active):
curl -fsSL https://raw.githubusercontent.com/ag4267research1/Quantum-Algorithms/main/ibm_check/check_ibm.py | python -
```

Simulators need no account.

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
├── hsp/                        # Hidden Subgroup Problem algorithms
│   ├── dj_hsp/                  # Deutsch / Deutsch-Jozsa
│   │   ├── oracle.py            # dj_oracle() + verify_promise()
│   │   ├── deutsch_jozsa.py     # build_circuit(), run_deutsch_jozsa(), run_shots_sweep()
│   │   ├── classical.py         # classical_f() + run_classical_deutsch_jozsa(): the classical solver
│   │   ├── run.py               # CLI: reads config.yaml, runs (or sweeps), saves results
│   │   └── config.yaml          # n, kind, secret, seed, shots, backend, memory,
│   │                            # results_dir, shots_sweep
│   ├── cluster/                  # Slurm sweep over n and shots for dj_hsp
│   │   ├── generate_jobs.sh      # writes runs/n<N>_shots<S>/{config.yaml,job.slurm}
│   │   └── submit_all.sh         # sbatch's every job.slurm it finds
│   └── demo/                     # class demo configs: one per algorithm x promise case
│       ├── deutsch_constant.yaml
│       ├── deutsch_balanced.yaml
│       ├── deutsch_jozsa_constant.yaml
│       └── deutsch_jozsa_balanced.yaml
├── docs/                      # Sphinx documentation (published to GitHub Pages)
│   ├── index.rst              # landing page
│   ├── conf.py
│   ├── requirements.txt       # docs build only; users do not need Sphinx
│   ├── assets/
│   │   └── mainpage.png        # banner image on the landing page
│   ├── _static/
│   │   └── custom.css
│   ├── setup/
│   │   ├── python.rst         # Python and Qiskit setup
│   │   ├── conda.rst          # Miniconda tutorial
│   │   └── cpp.rst            # Qiskit C++ and Armadillo setup
│   ├── ibm_setup/
│   │   ├── open_plan.rst      # IBM Quantum account and Open Plan
│   │   ├── credentials.rst    # API key, saving credentials, first connection
│   │   └── check.rst          # using ibm_check to verify setup and list QPUs
│   ├── concepts/
│   │   └── configuration.rst  # keeping experiments in YAML, not in code
│   └── algorithms/
│       ├── index.rst           # algorithms landing page
│       └── hsp/
│           ├── index.rst       # Hidden Subgroup Problem category page
│           ├── deutsch_jozsa.rst
│           └── cluster.rst     # using hsp/cluster/ to sweep n and shots on Slurm
├── .github/
│   └── workflows/
│       └── docs.yml           # builds and deploys the docs to GitHub Pages
└── .readthedocs.yaml
```

Created locally and not committed: `third_party/` (Qiskit and Qiskit C++ sources), `build/`,
any `results/` an algorithm's `run.py` writes (for example `hsp/dj_hsp/results/`), and
`hsp/cluster/runs/` (created by `generate_jobs.sh`).
