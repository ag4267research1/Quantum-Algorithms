#!/usr/bin/env python3
"""Check that the Python setup works and list the IBM QPUs you can use.

Read-only: it submits no jobs and uses none of your Open Plan minutes.

Usage:
    conda activate qalgos
    python ibm_check/check_ibm.py              # default saved account
    python ibm_check/check_ibm.py --name qalgos
    python ibm_check/check_ibm.py --include-simulators
"""

import argparse
import sys
from importlib import metadata

OK, BAD = "[ ok ]", "[FAIL]"
failures = 0


def report(ok, msg):
    global failures
    if not ok:
        failures += 1
    print(f"{OK if ok else BAD} {msg}")


def check_packages():
    print("\n1. Packages")
    for pkg in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime", "numpy", "pyyaml"):
        try:
            report(True, f"{pkg} {metadata.version(pkg)}")
        except metadata.PackageNotFoundError:
            report(False, f"{pkg} is not installed (run ./install.sh, then conda activate qalgos)")
    try:
        major = int(metadata.version("qiskit").split(".")[0])
        if major < 2:
            report(False, "qiskit >= 2 is required")
    except metadata.PackageNotFoundError:
        pass


def check_simulator():
    print("\n2. Local simulator (no account needed)")
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator

        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        sim = AerSimulator()
        counts = sim.run(transpile(qc, sim), shots=1000, seed_simulator=1).result().get_counts()
        good = set(counts) <= {"00", "11"} and sum(counts.values()) == 1000
        report(good, f"Bell-state test on AerSimulator: {dict(sorted(counts.items()))}")
    except Exception as e:  # noqa: BLE001
        report(False, f"simulator test failed: {e}")


def connect(name):
    print("\n3. IBM Quantum credentials")
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as e:
        report(False, f"cannot import qiskit_ibm_runtime: {e}")
        return None
    try:
        service = QiskitRuntimeService(name=name) if name else QiskitRuntimeService()
    except Exception as e:  # noqa: BLE001
        report(False, f"could not create the service: {e}")
        print(
            "       Fix: save your credentials (see docs: IBM setup > Credentials),\n"
            "       or set QISKIT_IBM_TOKEN and QISKIT_IBM_INSTANCE."
        )
        return None
    report(True, "connected to IBM Quantum Platform")
    try:
        acct = service.active_account() or {}
        for key in ("channel", "instance", "url"):
            if acct.get(key):
                print(f"       {key}: {acct[key]}")
    except Exception:  # noqa: BLE001
        pass  # never print the token
    return service


def list_qpus(service, include_simulators):
    print("\n4. Available backends")
    try:
        backends = service.backends(simulator=None if include_simulators else False)
    except Exception as e:  # noqa: BLE001
        report(False, f"could not list backends: {e}")
        return
    if not backends:
        report(False, "no backends available to this instance (check account, region and instance CRN)")
        return
    rows = []
    for b in backends:
        try:
            st = b.status()
            state = "online" if st.operational else "offline"
            pending = st.pending_jobs
        except Exception:  # noqa: BLE001
            state, pending = "unknown", -1
        proc = getattr(b, "processor_type", None) or {}
        family = proc.get("family", "") if isinstance(proc, dict) else str(proc)
        rows.append((b.name, b.num_qubits, family, state, pending))
    rows.sort(key=lambda r: (r[3] != "online", r[4] if r[4] >= 0 else 10**9, r[0]))

    print(f"       {'name':<20}{'qubits':>7}  {'processor':<12}{'status':<9}{'queue':>6}")
    for name, nq, fam, state, pend in rows:
        q = "-" if pend < 0 else str(pend)
        print(f"       {name:<20}{nq:>7}  {fam:<12}{state:<9}{q:>6}")
    online = [r for r in rows if r[3] == "online"]
    report(bool(online), f"{len(online)} of {len(rows)} backends online")
    if online:
        print(f"       shortest queue: {online[0][0]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help="name of the saved account (see save_account)")
    ap.add_argument("--include-simulators", action="store_true", help="also list IBM cloud simulators")
    args = ap.parse_args()

    print("IBM setup check (no jobs are submitted, no QPU time is used)")
    check_packages()
    check_simulator()
    service = connect(args.name)
    if service is not None:
        list_qpus(service, args.include_simulators)

    print()
    if failures:
        print(f"{failures} check(s) failed. See the messages above.")
        sys.exit(1)
    print("Everything works.")


if __name__ == "__main__":
    main()
