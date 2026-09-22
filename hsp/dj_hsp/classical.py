#!/usr/bin/env python3
"""Classical (non-quantum) solver for the Deutsch / Deutsch-Jozsa promise
problem: decide whether f is constant or balanced -- without a qubit
circuit, a simulator, or Qiskit's `QuantumCircuit` at all.

Same problem as deutsch_jozsa.py, solved by evaluating f classically at a
sequence of inputs. The deterministic classical algorithm needs, in the
worst case, 2**(n-1) + 1 queries: query x = 0, 1, 2, ... in order and stop
the moment two different outputs are seen (f is balanced), or once
2**(n-1) + 1 queries have all agreed (f must be constant). That bound
works because a balanced f is 0 on exactly half of the 2**n inputs and 1 on
the other half (by the promise); by the pigeonhole principle, more than
half of the inputs agreeing on one value is only possible if f is constant.

The quantum algorithm decides the same question in exactly 1 query,
regardless of n -- this file exists to make that contrast concrete for a
class demo: run both against the same config.yaml and compare.

Reads the same n/kind/secret/constant_value/seed as oracle.py and
deutsch_jozsa.py. config.yaml's other fields (shots, backend, memory,
shots_sweep) are for the quantum run only and are simply ignored here, so
the exact same config.yaml used for run.py can be pointed at this script.

Usage:
    conda activate qalgos
    python hsp/dj_hsp/classical.py                    # uses config.yaml next to this file
    python hsp/dj_hsp/classical.py path/to/other.yaml
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml

from oracle import OracleConfig


def _resolve_secret(n: int, kind: str, secret: str | None, seed: int | None) -> str | None:
    """Match oracle.py's dj_oracle(): pick the same random nonzero n-bit
    secret from the same seed when kind=balanced and no secret is given, so
    a classical run and a quantum run given the same config.yaml test the
    identical hidden oracle. Returns None when kind=constant."""
    if kind != "balanced":
        return None
    if secret is not None:
        if len(secret) != n or any(c not in "01" for c in secret) or secret == "0" * n:
            raise ValueError(f"secret must be a nonzero {n}-bit binary string, got {secret!r}")
        return secret
    rng = random.Random(seed)
    return format(rng.randint(1, 2**n - 1), f"0{n}b")


def classical_f(x: int, kind: Literal["constant", "balanced"], secret: str | None, constant_value: int) -> int:
    """The classical function the oracle implements, evaluated directly at
    one input x (0 <= x < 2**n) -- plain Python, no circuit."""
    if kind == "constant":
        return constant_value
    s = int(secret[::-1], 2)  # secret[i] lines up with qubit i, same as oracle.py's dj_oracle
    return bin(x & s).count("1") % 2


def run_classical_deutsch_jozsa(
    n: int,
    kind: Literal["constant", "balanced"] = "balanced",
    secret: str | None = None,
    constant_value: int = 0,
    seed: int | None = None,
) -> dict:
    """Decide constant vs balanced classically: query f at x=0,1,2,... in
    order, stopping the moment two different outputs are seen (balanced),
    or once 2**(n-1)+1 queries have all agreed (constant -- the worst case).

    Returns a dict with the oracle metadata (the same shape as
    run_deutsch_jozsa's "oracle" key, so a classical and a quantum run are
    easy to compare), every (x, f(x)) query made, how many queries that
    took, the worst-case bound, and the verdict.
    """
    if n < 1:
        raise ValueError("n must be >= 1 (n=1 is Deutsch's algorithm)")
    if kind == "constant" and constant_value not in (0, 1):
        raise ValueError("constant_value must be 0 or 1")

    secret = _resolve_secret(n, kind, secret, seed)
    oracle_meta = {
        "n": n,
        "kind": kind,
        "constant_value": constant_value if kind == "constant" else None,
        "secret": secret,
    }

    worst_case = 2 ** (n - 1) + 1
    queries: list[tuple[int, int]] = []
    first_value = None
    verdict = "constant"
    for x in range(2**n):
        y = classical_f(x, kind, secret, constant_value)
        queries.append((x, y))
        if first_value is None:
            first_value = y
        elif y != first_value:
            verdict = "balanced"
            break
        if len(queries) >= worst_case:
            verdict = "constant"
            break

    return {
        "n": n,
        "oracle": oracle_meta,
        "queries": queries,
        "num_queries": len(queries),
        "worst_case_queries": worst_case,
        "verdict": verdict,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", nargs="?", default=str(Path(__file__).parent / "config.yaml"))
    args = parser.parse_args()

    with open(args.config) as f:
        raw = yaml.safe_load(f)
    cfg = OracleConfig(**raw)
    # Same key run.py uses; missing or null both mean "don't save".
    results_dir = raw.get("results_dir", "results")

    label = "Deutsch" if cfg.n == 1 else "Deutsch-Jozsa"
    result = run_classical_deutsch_jozsa(
        cfg.n, kind=cfg.kind, secret=cfg.secret, constant_value=cfg.constant_value, seed=cfg.seed
    )
    oracle_meta = result["oracle"]

    print(f"{label} algorithm, classical solver: n={cfg.n}")
    if oracle_meta["kind"] == "constant":
        print(f"oracle: kind=constant  constant_value={oracle_meta['constant_value']}")
    else:
        print(f"oracle: kind=balanced  secret={oracle_meta['secret']}")

    print(
        f"queries used: {result['num_queries']} "
        f"(worst-case bound: {result['worst_case_queries']} = 2^(n-1)+1, "
        f"out of 2^n = {2 ** cfg.n} possible inputs)"
    )
    print(f"result: f is {result['verdict'].upper()}")
    print("(the quantum algorithm decides this with exactly 1 query, regardless of n)")

    if results_dir:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        payload = {
            "timestamp": timestamp,
            "config": {
                "n": cfg.n,
                "kind": cfg.kind,
                "constant_value": cfg.constant_value,
                "secret": cfg.secret,
                "seed": cfg.seed,
            },
            "oracle": oracle_meta,
            "num_queries": result["num_queries"],
            "worst_case_queries": result["worst_case_queries"],
            "verdict": result["verdict"],
        }
        out_dir = Path(results_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"n{cfg.n}_{oracle_meta['kind']}_classical_{timestamp}.json"
        with open(path, "w") as fp:
            json.dump(payload, fp, indent=2, default=str)
        print(f"saved: {path}")


if __name__ == "__main__":
    main()
