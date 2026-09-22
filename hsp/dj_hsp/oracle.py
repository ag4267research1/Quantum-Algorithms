#!/usr/bin/env python3
"""One oracle generator for Deutsch's algorithm and Deutsch-Jozsa.

n = 1 is exactly Deutsch's algorithm. n > 1 is Deutsch-Jozsa. Both use the
same promise, so both are built by the same function, `dj_oracle`.

The oracle acts on n input qubits (x) plus 1 output qubit (y), implementing
    |x>|y> -> |x>|y XOR f(x)>
for one of:
    kind="constant"  f(x) is the same value (0 or 1) for every x
    kind="balanced"  f(x) = XOR of the bits of x where s has a 1, for a
                      fixed nonzero n-bit string s. Flipping any one input
                      bit where s is 1 always flips the output, which pairs
                      up all 2**n inputs into 0/1 pairs -- so this is
                      balanced for *any* nonzero s, no need to check case
                      by case.

These are the only two cases Deutsch-Jozsa's promise allows -- there is no
third "kind" of f, so none is offered here.

Only CNOT/X gates are used, so it is O(n) gates for any n.

Usage:
    conda activate qalgos
    python hsp/dj_hsp/oracle.py                    # uses config.yaml next to this file
    python hsp/dj_hsp/oracle.py path/to/other.yaml
    python hsp/dj_hsp/oracle.py --no-verify config.yaml
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


class OracleConfig(BaseModel):
    """The knobs that define one Deutsch / Deutsch-Jozsa oracle instance."""

    n: int = Field(ge=1, description="input qubits; n=1 is Deutsch's algorithm, n>1 is Deutsch-Jozsa")
    kind: Literal["constant", "balanced"] = "balanced"
    constant_value: int = Field(default=0, ge=0, le=1, description="used only when kind=constant")
    secret: str | None = Field(default=None, description="nonzero n-bit binary string; used only when kind=balanced")
    seed: int | None = Field(default=None, description="reproducible random secret, when kind=balanced and secret is not given")


def dj_oracle(
    n: int,
    kind: Literal["constant", "balanced"] = "balanced",
    secret: str | None = None,
    constant_value: int = 0,
    seed: int | None = None,
) -> tuple[QuantumCircuit, dict]:
    """Build a Deutsch / Deutsch-Jozsa oracle on n input qubits + 1 output qubit.

    Qubits 0..n-1 are x, qubit n is y. Guaranteed to satisfy the promise:
    constant on every input, or balanced (0 on exactly 2**(n-1) inputs).

    Returns (circuit, metadata) where metadata records what was actually
    built (useful when secret was left to be chosen for you).
    """
    if n < 1:
        raise ValueError("n must be >= 1 (n=1 is Deutsch's algorithm)")

    rng = random.Random(seed)

    qc = QuantumCircuit(n + 1, name=f"U_f(n={n},{kind})")

    if kind == "constant":
        if constant_value not in (0, 1):
            raise ValueError("constant_value must be 0 or 1")
        if constant_value == 1:
            qc.x(n)
        meta = {"n": n, "kind": "constant", "constant_value": constant_value, "secret": None}

    elif kind == "balanced":
        if secret is None:
            secret = format(rng.randint(1, 2**n - 1), f"0{n}b")
        if len(secret) != n or any(c not in "01" for c in secret) or secret == "0" * n:
            raise ValueError(f"secret must be a nonzero {n}-bit binary string, got {secret!r}")
        for i, bit in enumerate(secret):
            if bit == "1":
                qc.cx(i, n)
        meta = {"n": n, "kind": "balanced", "constant_value": None, "secret": secret}

    else:
        raise ValueError(f"unknown kind {kind!r}; use 'constant' or 'balanced'")

    return qc, meta


def verify_promise(qc: QuantumCircuit, n: int) -> str:
    """Brute-force check (2**n circuit evaluations) that qc's classical
    function is constant or balanced. Returns "constant" or "balanced";
    raises AssertionError if the promise is violated. Only practical for
    small n -- this is a correctness check on the oracle, not something to
    run inside the quantum algorithm itself.
    """
    ones = 0
    for x in range(2**n):
        bits = format(x, f"0{n}b")
        prep = QuantumCircuit(n + 1)
        for i, b in enumerate(bits):
            if b == "1":
                prep.x(i)
        sv = Statevector.from_label("0" * (n + 1)).evolve(prep.compose(qc))
        probs = sv.probabilities_dict()
        bitstring = max(probs, key=probs.get)  # deterministic outcome, up to fp noise
        y = int(bitstring[0])  # qiskit orders bitstrings with qubit n (leftmost) first
        ones += y

    if ones == 0 or ones == 2**n:
        return "constant"
    if ones == 2 ** (n - 1):
        return "balanced"
    raise AssertionError(f"oracle violates the Deutsch-Jozsa promise: f(x)=1 on {ones}/{2**n} inputs")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", nargs="?", default=str(Path(__file__).parent / "config.yaml"))
    parser.add_argument("--no-verify", action="store_true", help="skip the brute-force promise check")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = OracleConfig(**yaml.safe_load(f))

    qc, meta = dj_oracle(
        cfg.n, kind=cfg.kind, secret=cfg.secret, constant_value=cfg.constant_value, seed=cfg.seed
    )

    label = "Deutsch" if meta["n"] == 1 else "Deutsch-Jozsa"
    print(f"{label} oracle: n={meta['n']}  kind={meta['kind']}")
    if meta["kind"] == "constant":
        print(f"constant_value = {meta['constant_value']}")
    else:
        print(f"secret s = {meta['secret']}")
    print(qc.draw(output="text"))

    if args.no_verify:
        return
    if cfg.n > 12:
        print(f"promise check: skipped (n={cfg.n} is too large to brute force)")
        return
    result = verify_promise(qc, cfg.n)
    print(f"promise check: PASSED ({result})")


if __name__ == "__main__":
    main()
