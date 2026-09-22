Check your setup and list QPUs
==============================

The repository ships a small script, ``ibm_check/check_ibm.py``, that tells
you whether your setup works and which IBM QPUs your instance can use. Run it
after :doc:`credentials`, and any time something stops working.

.. note::

   Like the rest of this section, the checker is for the **Python** track
   only, for now.

It is read-only: it submits no jobs and uses none of your Open Plan minutes.
It never prints your API key.

Run it
------

With the ``qalgos`` environment active, from the repository root:

.. code-block:: bash

   python ibm_check/check_ibm.py

Or without cloning the repository:

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/ag4267research1/Quantum-Algorithms/main/ibm_check/check_ibm.py | python -

Options:

.. code-block:: bash

   python ibm_check/check_ibm.py --name qalgos           # a named saved account
   python ibm_check/check_ibm.py --include-simulators    # also list IBM cloud simulators

The exit code is ``0`` when everything passes and ``1`` otherwise, so you can
use it in scripts.

What it checks
--------------

1. **Packages.** Qiskit, Qiskit Aer, ``qiskit-ibm-runtime``, numpy and pyyaml
   are installed, and Qiskit is version 2 or newer.
2. **Local simulator.** A Bell-state circuit runs on ``AerSimulator``. This
   needs no account, so it tells you the Python side works even if IBM does
   not.
3. **Credentials.** It connects to the IBM Quantum Platform with your saved
   account, or with ``QISKIT_IBM_TOKEN`` and ``QISKIT_IBM_INSTANCE``, and
   prints the channel and instance it used.
4. **QPUs.** It lists the backends your instance can use: name, number of
   qubits, processor family, online or offline, and queue length. The list is
   sorted with online devices and the shortest queue first, and the script
   names the least busy one.

Reading the output
------------------

The lines look like this (the QPU names and numbers are illustrative; yours
will differ):

.. code-block:: text

   1. Packages
   [ ok ] qiskit 2.5.2
   [ ok ] qiskit-aer 0.17.2
   [ ok ] qiskit-ibm-runtime 0.49.0
   ...
   2. Local simulator (no account needed)
   [ ok ] Bell-state test on AerSimulator: {'00': 491, '11': 509}

   4. Available backends
          name                 qubits  processor   status    queue
          ibm_example_a           156  Heron       online        3
          ibm_example_b           127  Eagle       online       41
   [ ok ] 2 of 2 backends online
          shortest queue: ibm_example_a

   Everything works.

Any line that starts with ``[FAIL]`` explains what is wrong.

If a check fails
----------------

Check 1 fails
   Run ``./install.sh`` and ``conda activate qalgos``, then try again.

Check 2 fails
   Qiskit Aer is broken or missing. Reinstall it with
   ``pip install --force-reinstall qiskit-aer``.

Check 3 fails with ``Unable to find account``
   No credentials are saved, or you used a different ``name``. See
   :doc:`credentials`.

Check 3 fails with an authentication error
   The API key is wrong or was deleted. Create a new one on the Platform
   dashboard and save it again.

Check 4 lists no backends
   Check the account and region switchers on the Platform, and that the
   ``instance`` you saved is the CRN of an Open Plan instance you can access.

Everything is offline
   The devices may be in maintenance. Check the Platform dashboard and try
   again later.
