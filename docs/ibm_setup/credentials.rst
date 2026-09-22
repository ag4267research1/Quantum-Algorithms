Credentials and first connection
================================

This page assumes you finished :doc:`open_plan` and have the ``qalgos``
environment active. ``qiskit-ibm-runtime`` is already installed there.

.. note::

   This page is for the **Python** track only, for now. Running on IBM
   hardware from C++ is not set up yet.

Get your API key
----------------

1. Log in at https://quantum.cloud.ibm.com.
2. On the dashboard, find the **API key** panel and create a key. Copy it
   right away and store it in a password manager.
3. Open https://quantum.cloud.ibm.com/instances and copy the **CRN** (or the
   name) of your Open Plan instance.

.. warning::

   The API key is a password. Never commit it to git, paste it into a YAML
   file that is committed, or share it in screenshots. If it leaks, delete it
   on the dashboard and create a new one.

Save the credentials on your machine
------------------------------------

Do this once, on a personal computer you trust:

.. code-block:: python

   from qiskit_ibm_runtime import QiskitRuntimeService

   QiskitRuntimeService.save_account(
       token="<your-api-key>",
       instance="<CRN or instance name>",
       name="qalgos",
       set_as_default=True,
       overwrite=True,
   )

This writes the credentials to ``~/.qiskit/qiskit-ibm.json``. After that, no
script needs the key in its source. To have Qiskit pick a plan for you
instead of naming an instance, use ``plans_preference=["open"]`` and
``region="us-east"``.

Do not use ``save_account`` on shared or untrusted machines. Use environment
variables there:

.. code-block:: bash

   export QISKIT_IBM_TOKEN="<your-api-key>"
   export QISKIT_IBM_INSTANCE="<CRN or instance name>"

This is also the right way to keep the key out of the repository, as
recommended on the :doc:`configuration page </concepts/configuration>`.

Check the connection
--------------------

.. code-block:: python

   from qiskit_ibm_runtime import QiskitRuntimeService

   service = QiskitRuntimeService()           # uses the saved default
   # service = QiskitRuntimeService(name="qalgos")   # or a named account

   print(service.saved_accounts())            # what is stored locally
   for backend in service.backends():
       print(backend.name, backend.num_qubits)

The repository also ships a ready-made checker that verifies your packages,
the simulator and your credentials, and lists the QPUs you can use. See
:doc:`check`.

If the list of backends prints, you are connected. If it fails:

``Unable to find account``
   No credentials were saved, or you used a different ``name``. Run
   ``save_account`` again.

Authentication or 401 errors
   The API key is wrong or was deleted. Create a new one.

No backends returned, or wrong instance
   Check the account and region switchers on the Platform, and that
   ``instance`` is the CRN of an instance you can access.

Using the Open Plan budget wisely
---------------------------------

* Develop and debug on ``AerSimulator`` or a fake backend from
  ``qiskit_ibm_runtime.fake_provider``. Both are free and unlimited.
* Transpile locally, run on hardware only for the final experiment.
* Keep shots modest. Watch the remaining minutes on the dashboard.
* Save each hardware result together with its YAML config, so a run is never
  repeated by accident.

References
----------

* `Save your login credentials
  <https://quantum.cloud.ibm.com/docs/en/guides/save-credentials>`_
* `Initialize your service
  <https://quantum.cloud.ibm.com/docs/en/guides/initialize-account>`_
* `Create and manage instances
  <https://quantum.cloud.ibm.com/docs/en/guides/instances>`_
* `Plans overview
  <https://quantum.cloud.ibm.com/docs/en/guides/plans-overview>`_
