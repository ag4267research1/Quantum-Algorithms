#!/usr/bin/env python3
"""Run the Deutsch / Deutsch-Jozsa algorithm from a YAML config.

Reads the same config.yaml as oracle.py (n, kind, secret, constant_value,
seed) plus `shots`, `backend`, `memory`, `results_dir` and `shots_sweep`,
builds the oracle for that n, runs the algorithm, and prints the
measurement result.

With `shots_sweep` set to a list of shot counts, it instead runs the same
oracle at each shot count and compares measured accuracy across them,
writing an .xlsx file. Otherwise it runs once at `shots` and, unless
`results_dir` is null, saves a JSON file recording exactly what was run.

Usage:
    conda activate qalgos
    python hsp/dj_hsp/run.py                    # uses config.yaml next to this file
    python hsp/dj_hsp/run.py path/to/other.yaml
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from pydantic import Field, field_validator

from deutsch_jozsa import AER_METHODS, run_deutsch_jozsa, run_shots_sweep
from oracle import OracleConfig


class RunConfig(OracleConfig):
    shots: int = Field(default=1024, gt=0, description="number of circuit measurements for a single run")
    backend: str = Field(default="aer_simulator", description=f"one of {sorted(AER_METHODS)}")
    memory: bool = Field(
        default=False, description="store every shot's individual outcome, not just the aggregated counts"
    )
    results_dir: str | None = Field(
        default="results",
        description="folder to save run output in; relative paths resolve against the "
        "current working directory; set to null to not save anything",
    )
    shots_sweep: list[int] | None = Field(
        default=None,
        description="a list of shot counts to compare accuracy across (writes results_dir/*.xlsx "
        "instead of running once at `shots`)",
    )

    @field_validator("shots_sweep")
    @classmethod
    def _validate_shots_sweep(cls, v: list[int] | None) -> list[int] | None:
        if v is not None:
            if not v:
                raise ValueError("shots_sweep must not be empty when given")
            if any(s <= 0 for s in v):
                raise ValueError("every value in shots_sweep must be > 0")
        return v


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", nargs="?", default=str(Path(__file__).parent / "config.yaml"))
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = RunConfig(**yaml.safe_load(f))

    label = "Deutsch" if cfg.n == 1 else "Deutsch-Jozsa"
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    base = f"n{cfg.n}_{cfg.kind}_{timestamp}"

    if cfg.shots_sweep:
        rows = run_shots_sweep(
            cfg.n,
            kind=cfg.kind,
            secret=cfg.secret,
            constant_value=cfg.constant_value,
            seed=cfg.seed,
            shots_list=cfg.shots_sweep,
            backend=cfg.backend,
        )
        print(f"{label} accuracy vs shots: n={cfg.n}  kind={cfg.kind}  backend={cfg.backend}")
        for r in rows:
            print(f"  shots={r['shots']:<8} accuracy={r['accuracy']:.4f}  verdict={r['verdict']}")

        if cfg.results_dir is not None:
            out_dir = Path(cfg.results_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            xlsx_path = out_dir / f"accuracy_vs_shots_{base}.xlsx"
            pd.DataFrame(rows).to_excel(xlsx_path, sheet_name="accuracy_vs_shots", index=False)
            _save_json(out_dir / f"accuracy_vs_shots_{base}.config.json", cfg.model_dump())
            print(f"saved: {xlsx_path}")
        return

    result = run_deutsch_jozsa(
        cfg.n,
        kind=cfg.kind,
        secret=cfg.secret,
        constant_value=cfg.constant_value,
        seed=cfg.seed,
        shots=cfg.shots,
        backend=cfg.backend,
        memory=cfg.memory,
    )

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

    if cfg.results_dir is not None:
        payload = {
            "timestamp": timestamp,
            "config": cfg.model_dump(),
            "oracle": oracle_meta,
            "counts": result["counts"],
            "verdict": result["verdict"],
        }
        if cfg.memory:
            payload["memory"] = result["memory"]
        json_path = Path(cfg.results_dir) / f"{base}.json"
        _save_json(json_path, payload)
        print(f"saved: {json_path}")


if __name__ == "__main__":
    main()
