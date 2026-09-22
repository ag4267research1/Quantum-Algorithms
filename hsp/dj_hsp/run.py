#!/usr/bin/env python3
"""Run the Deutsch / Deutsch-Jozsa algorithm from a YAML config.

Reads the same config.yaml as oracle.py (n, kind, secret, constant_value,
seed) plus `shots` and `backend`, builds the oracle for that n, runs the
algorithm, and prints the measurement result.

Usage:
    conda activate qalgos
    python hsp/dj_hsp/run.py                    # uses config.yaml next to this file
    python hsp/dj_hsp/run.py path/to/other.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from pydantic import Field

from deutsch_jozsa import AER_METHODS, run_deutsch_jozsa
from oracle import OracleConfig


class RunConfig(OracleConfig):
    shots: int = Field(default=1024, gt=0, description="number of circuit measurements")
    backend: str = Field(default="aer_simulator", description=f"one of {sorted(AER_METHODS)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", nargs="?", default=str(Path(__file__).parent / "config.yaml"))
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = RunConfig(**yaml.safe_load(f))

    result = run_deutsch_jozsa(
        cfg.n,
        kind=cfg.kind,
        secret=cfg.secret,
        constant_value=cfg.constant_value,
        seed=cfg.seed,
        shots=cfg.shots,
        backend=cfg.backend,
    )

    label = "Deutsch" if cfg.n == 1 else "Deutsch-Jozsa"
    oracle_meta = result["oracle"]

    print(f"{label} algorithm: n={cfg.n}  shots={cfg.shots}  backend={cfg.backend}")
    if oracle_meta["kind"] == "constant":
        print(f"oracle: kind=constant  constant_value={oracle_meta['constant_value']}")
    else:
        print(f"oracle: kind=balanced  secret={oracle_meta['secret']}")

    print(f"measurement counts: {result['counts']}")
    print(f"result: f is {result['verdict'].upper()}")
    if oracle_meta["kind"] == "balanced" and cfg.n > 1:
        print("(qiskit prints bitstrings with qubit 0 on the right, so this "
              "reads as the secret above reversed)")


if __name__ == "__main__":
    main()
