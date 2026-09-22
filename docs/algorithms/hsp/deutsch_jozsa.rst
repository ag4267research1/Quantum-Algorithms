Deutsch / Deutsch-Jozsa
========================

``n = 1`` is Deutsch's algorithm. ``n > 1`` is Deutsch-Jozsa. Same code
either way. The code lives in ``hsp/dj_hsp/``.

The problem
------------

You are given a function :math:`f: \{0,1\}^n \to \{0,1\}` as a black box,
with a promise: :math:`f` is either

* **constant** -- the same value for every input, or
* **balanced** -- 0 for exactly half of the :math:`2^n` inputs and 1 for
  the other half.

Classically, deciding which one it is can take up to :math:`2^{n-1}+1`
queries in the worst case. The quantum algorithm always decides it with
**one** query to the oracle.

The oracle
----------

``hsp/dj_hsp/oracle.py`` builds a reversible circuit
``U_f : |x>|y> -> |x>|y XOR f(x)>`` on ``n`` input qubits (``x``) plus 1
output qubit (``y``), via ``dj_oracle(n, kind, secret, constant_value, seed)``:

* ``kind="constant"`` -- ``f(x)`` is the same value for every ``x``. Built
  with an ``X`` on ``y`` (or nothing, for the all-zero case).
* ``kind="balanced"`` -- ``f(x)`` is the XOR of the bits of ``x`` where a
  fixed nonzero string ``s`` has a 1. Built with one ``CNOT(x_i, y)`` per
  ``1`` bit in ``s``. Flipping any input bit where ``s`` is 1 always flips
  the output, which pairs up all :math:`2^n` inputs into 0/1 pairs -- so
  this is balanced for *any* nonzero ``s``, with nothing to check case by
  case.
* ``kind="random"`` -- picks constant or balanced at random (seeded).

``verify_promise()`` brute-force simulates the built circuit over all
:math:`2^n` inputs and confirms it really is constant or balanced. It runs
automatically when you call ``oracle.py`` directly, for ``n`` up to 12.

The algorithm
--------------

``hsp/dj_hsp/deutsch_jozsa.py`` wraps the oracle in the standard circuit:

.. code-block:: text

   x (n qubits): |0> --H--[ oracle ]--H--measure
   y (1 qubit):  |0> --X----H---------[ oracle ]

``y`` is prepared as :math:`|-\rangle` (``X`` then ``H``), so the oracle
leaves a phase :math:`(-1)^{f(x)}` on :math:`|x\rangle` instead of flipping
a qubit (phase kickback). After the second round of ``H`` gates on ``x``:

* measuring **all zeros** means :math:`f` is **constant**
* measuring **anything else** means :math:`f` is **balanced**

``run_deutsch_jozsa(n, kind, secret, constant_value, seed, shots, backend, memory)``
builds the oracle for that exact ``n``, runs the circuit ``shots`` times on
``AerSimulator``, and returns the verdict along with the measurement counts
(and, with ``memory=True``, every individual shot's outcome). Because the
same ``n`` builds both the oracle and the algorithm circuit, they can never
end up sized differently.

``run_shots_sweep(n, kind, secret, constant_value, seed, shots_list, backend)``
builds the oracle **once** and runs it at each shot count in ``shots_list``,
reporting what fraction of shots landed on the expected outcome (the
oracle's ``0``\ s for constant, the secret reversed for balanced) at each
count -- see :ref:`dj-accuracy-vs-shots`.

Files
-----

.. code-block:: text

   hsp/dj_hsp/
   ├── oracle.py          # dj_oracle() + verify_promise()
   ├── deutsch_jozsa.py   # build_circuit(), run_deutsch_jozsa(), run_shots_sweep()
   ├── run.py             # CLI: reads config.yaml, runs (or sweeps), saves results
   └── config.yaml        # n, kind, secret, seed, shots, backend, memory,
                           # results_dir, shots_sweep

Configuration
-------------

One YAML file drives both the oracle and the algorithm (see
:doc:`/concepts/configuration`):

.. code-block:: yaml

   n: 4               # input qubits (1 = Deutsch, >1 = Deutsch-Jozsa)
   kind: balanced     # constant | balanced | random
   constant_value: 0  # 0 or 1, used when kind=constant
   secret: null       # n-bit binary string, used when kind=balanced
   seed: 7            # random secret / random kind choice
   shots: 1024        # measurements for a single run (ignored if shots_sweep is set)
   backend: aer_simulator
   memory: false      # store every shot's individual outcome, not just aggregated counts
   results_dir: results   # where run.py saves output; relative to the current directory,
                           # or an absolute path; set to null to not save anything
   shots_sweep: null  # e.g. [64, 128, 256, 512, 1024] -- compare accuracy across shot
                       # counts instead of the single run above; see below

``backend`` accepts ``aer_simulator`` (the default) or a specific
``AerSimulator`` method: ``statevector``, ``density_matrix``,
``stabilizer``, ``matrix_product_state``, ``extended_stabilizer``,
``unitary``, ``superop``.

``memory`` stores each shot's own outcome (Qiskit's per-shot readout), not
only the aggregated ``counts``. It lets you check that every shot really did
agree, rather than trusting the counts dict alone.

``results_dir`` is where ``run.py`` saves what it produced. Leave it as
``results`` (created next to wherever you run the command from), point it
anywhere else, or set it to ``null`` to save nothing. Saving the exact config
next to the result is the rule described on
:doc:`the configuration page </concepts/configuration>`.

Run it
------

With the ``qalgos`` environment active, from the repository root:

.. code-block:: bash

   python hsp/dj_hsp/run.py                     # uses config.yaml next to run.py
   python hsp/dj_hsp/run.py path/to/other.yaml

To inspect just the oracle circuit (with the brute-force promise check):

.. code-block:: bash

   python hsp/dj_hsp/oracle.py

Reading the output
-------------------

.. code-block:: text

   Deutsch-Jozsa algorithm: n=4  shots=1024  backend=aer_simulator
   oracle: kind=balanced  secret=0110
   measurement counts: {'0110': 1024}
   result: f is BALANCED
   (qiskit prints bitstrings with qubit 0 on the right, so this reads as the secret above reversed)
   saved: results/n4_balanced_20260101T120000.json

The saved JSON has the config used, the oracle metadata, the counts, the
verdict, and (if ``memory: true``) every shot's own outcome -- everything
needed to reproduce the run.

.. _dj-accuracy-vs-shots:

Comparing accuracy across shot counts
--------------------------------------

Set ``shots_sweep`` in the config to a list of shot counts instead of
running once at ``shots``:

.. code-block:: yaml

   shots_sweep: [64, 128, 256, 512, 1024, 2048]

``run.py`` then builds the oracle once and runs it at each shot count,
recording what fraction of shots measured the expected outcome:

.. code-block:: text

   Deutsch-Jozsa accuracy vs shots: n=4  kind=balanced  backend=aer_simulator
     shots=64       accuracy=1.0000  verdict=balanced
     shots=256      accuracy=1.0000  verdict=balanced
     shots=1024     accuracy=1.0000  verdict=balanced
   saved: results/accuracy_vs_shots_n4_balanced_20260101T120000.xlsx

The ``.xlsx`` has one row per shot count (``shots``, ``accuracy``, ``hits``,
``verdict``, ``distinct_outcomes``, ``top_outcome``); the config used is
saved next to it as a matching ``.config.json``.

In a noiseless simulation Deutsch-Jozsa is exact, so accuracy is 1.0 at
every shot count -- this is where the sweep is most useful once a noisy
backend (``density_matrix`` with a noise model, or real IBM hardware) is in
the mix, to see how many shots it takes for the majority answer to become
reliable.

All shots agree in this noiseless simulation -- that is the point of the
algorithm, one query settles it. The note about reversed bitstrings is a
Qiskit display convention (qubit 0 is the rightmost character), not an
error; if you compare the measured string to the secret printed above it,
reverse one of them first.
