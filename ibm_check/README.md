# ibm_check

Tells you whether your setup works and which IBM QPUs you can use.

```bash
conda activate qalgos
python ibm_check/check_ibm.py
```

Without cloning the repository (with the environment active):

```bash
curl -fsSL https://raw.githubusercontent.com/ag4267research1/Quantum-Algorithms/main/ibm_check/check_ibm.py | python -
```

It runs four checks:

1. **Packages**: Qiskit, Qiskit Aer and qiskit-ibm-runtime are installed.
2. **Local simulator**: a Bell-state circuit runs on `AerSimulator`. No account needed.
3. **Credentials**: connects to the IBM Quantum Platform with your saved account
   (or `QISKIT_IBM_TOKEN` and `QISKIT_IBM_INSTANCE`).
4. **QPUs**: lists the backends your instance can use, with qubits, processor
   family, online/offline status and queue length, shortest queue first.

The script is read-only. It submits no jobs and uses none of your Open Plan minutes.
It never prints your API key.

Options:

```bash
python ibm_check/check_ibm.py --name qalgos          # a named saved account
curl -fsSL https://raw.githubusercontent.com/ag4267research1/Quantum-Algorithms/main/ibm_check/check_ibm.py | python - --name qalgos
python ibm_check/check_ibm.py --include-simulators    # also list IBM cloud simulators
```

Exit code is `0` when everything passes and `1` otherwise.

If check 3 fails, follow the IBM setup guide:
http://theory-code.com/Quantum-Algorithms/ibm_setup/open_plan.html

This check covers the Python track only, for now.
