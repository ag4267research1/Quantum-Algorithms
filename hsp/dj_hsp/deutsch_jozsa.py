#!/usr/bin/env python3
"""Deutsch / Deutsch-Jozsa algorithm: decide constant vs balanced in one query.

n=1 is Deutsch's algorithm, n>1 is Deutsch-Jozsa -- same code either way.
The oracle is built from the *same* n passed in here (via dj_oracle in
oracle.py), so there's no separate "algorithm n" that could ever drift out
of sync with the oracle's n.

Circuit:
    x register (n qubits): |0> --H--[ oracle ]--H--measure
    y register (1 qubit):  |0> --X----H---------[ oracle ]
                            (prepared as |-> so the oracle leaves a phase
                            (-1)^f(x) on |x> instead of flipping a qubit)

Reading the result: after the H's, x measures as all zeros with certainty
if f is constant, and as *anything else* if f is balanced (every shot
agrees, in this noiseless simulation) -- that's the one-query trick.
"""

from __future__ import annotations

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import AerSimulator

from oracle import dj_oracle

# Accepted backend values. "aer_simulator" is the default AerSimulator; the
# rest force a specific internal simulation method.
AER_METHODS = frozenset(
    {
        "aer_simulator",
        "statevector",
        "density_matrix",
        "stabilizer",
        "matrix_product_state",
        "extended_stabilizer",
        "unitary",
        "superop",
    }
)


def build_circuit(n: int, oracle_qc: QuantumCircuit) -> QuantumCircuit:
    """Wrap an (n+1)-qubit oracle (n x qubits + 1 y qubit, as built by
    dj_oracle) into the full Deutsch-Jozsa circuit."""
    x = QuantumRegister(n, "x")
    y = QuantumRegister(1, "y")
    c = ClassicalRegister(n, "c")
    qc = QuantumCircuit(x, y, c)

    qc.x(y)
    qc.h(x)
    qc.h(y)

    qc.compose(oracle_qc, qubits=x[:] + y[:], inplace=True)

    qc.h(x)
    qc.measure(x, c)
    return qc


def expected_outcome(oracle_meta: dict) -> str:
    """The exact classical-register bitstring Deutsch-Jozsa should measure
    for the oracle described by `oracle_meta` (as returned by `dj_oracle`):
    all zeros for a constant oracle, or the secret read qubit-0-first (i.e.
    reversed) for a balanced one -- see the note in run.py's output."""
    n = oracle_meta["n"]
    if oracle_meta["kind"] == "constant":
        return "0" * n
    return oracle_meta["secret"][::-1]


def _verdict(counts: dict, n: int) -> str:
    return "constant" if set(counts) == {"0" * n} else "balanced"


def run_deutsch_jozsa(
    n: int,
    kind: str = "balanced",
    secret: str | None = None,
    constant_value: int = 0,
    seed: int | None = None,
    shots: int = 1024,
    backend: str = "aer_simulator",
    memory: bool = False,
) -> dict:
    """Build the oracle for `n`, run the Deutsch-Jozsa circuit on it `shots`
    times, and decide constant vs balanced from the measurement counts.

    With `memory=True`, also returns the ordered outcome of every individual
    shot (Qiskit's per-shot readout), not just the aggregated counts.

    Returns a dict with the oracle metadata, the measurement counts, and
    the verdict ("constant" or "balanced").
    """
    if backend not in AER_METHODS:
        raise ValueError(f"unknown backend {backend!r}; must be one of {sorted(AER_METHODS)}")

    oracle_qc, oracle_meta = dj_oracle(n, kind=kind, secret=secret, constant_value=constant_value, seed=seed)
    qc = build_circuit(n, oracle_qc)

    method = "automatic" if backend == "aer_simulator" else backend
    sim = AerSimulator(method=method)
    job_result = sim.run(transpile(qc, sim), shots=shots, memory=memory).result()
    counts = job_result.get_counts()

    result = {
        "n": n,
        "shots": shots,
        "backend": backend,
        "oracle": oracle_meta,
        "counts": counts,
        "verdict": _verdict(counts, n),
        "circuit": qc,
    }
    if memory:
        result["memory"] = job_result.get_memory()
    return result


def run_shots_sweep(
    n: int,
    kind: str = "balanced",
    secret: str | None = None,
    constant_value: int = 0,
    seed: int | None = None,
    shots_list: list[int] = (256, 1024),
    backend: str = "aer_simulator",
) -> list[dict]:
    """Run the *same* oracle at several shot counts and report, for each,
    what fraction of shots landed on the expected outcome -- i.e. how
    measured accuracy behaves as shots grows. The oracle is built once (from
    `n`, `kind`, `secret`/`constant_value`, `seed`) so every shot count is
    tested against an identical circuit.

    In a noiseless simulation Deutsch-Jozsa is exact, so accuracy is 1.0 at
    every shot count; the sweep becomes informative with a noisy backend
    (density_matrix with a noise model, or real IBM hardware).

    Returns one dict per shots value: shots, accuracy, hits, verdict,
    distinct_outcomes, top_outcome.
    """
    if backend not in AER_METHODS:
        raise ValueError(f"unknown backend {backend!r}; must be one of {sorted(AER_METHODS)}")
    if not shots_list:
        raise ValueError("shots_list must not be empty")

    oracle_qc, oracle_meta = dj_oracle(n, kind=kind, secret=secret, constant_value=constant_value, seed=seed)
    qc = build_circuit(n, oracle_qc)
    expected = expected_outcome(oracle_meta)

    method = "automatic" if backend == "aer_simulator" else backend
    sim = AerSimulator(method=method)
    transpiled = transpile(qc, sim)

    rows = []
    for shots in shots_list:
        counts = sim.run(transpiled, shots=shots).result().get_counts()
        hits = counts.get(expected, 0)
        rows.append(
            {
                "shots": shots,
                "accuracy": hits / shots,
                "hits": hits,
                "verdict": _verdict(counts, n),
                "distinct_outcomes": len(counts),
                "top_outcome": max(counts, key=counts.get),
            }
        )
    return rows
