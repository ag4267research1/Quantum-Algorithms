IBM Quantum account and Open Plan
=================================

To run circuits on real IBM quantum computers you need an account on the
**IBM Quantum Platform** and an **instance** on a pricing plan. The **Open
Plan** is free and is the right choice for learning and for the examples in
this repository. Simulators (Qiskit Aer, Armadillo) need no account at all.

.. note::

   IBM changes its sign-up flow and plan limits from time to time. The links
   in :ref:`ibm-references` are the authority. If a step here differs from
   what you see on screen, follow the screen and the IBM docs.

.. note::

   The IBM setup in this section is for the **Python** track only, for now.
   Running on IBM hardware from C++ is not set up yet.

What the Open Plan gives you
----------------------------

* **Cost:** free.
* **Usage:** up to **10 minutes of QPU time per 28-day rolling window**. IBM
  has also offered a limited-time opt-in for extra minutes to active Open Plan
  users. Check the plans page for the current offer.
* **Region:** Open Plan instances are available in ``us-east`` only.
* **Audience:** IBM recommends it for people learning quantum computing and
  exploring IBM's quantum technology.
* **Tracking:** your usage appears on the Platform dashboard and on the
  Workloads page.

Ten minutes sounds small, but a circuit run typically takes seconds of QPU
time. Test everything on a simulator first, then spend hardware time only on
the final runs.

Step 1: Create an IBM Cloud account
-----------------------------------

The IBM Quantum Platform sits on top of IBM Cloud, so you need an IBM Cloud
account first.

1. Go to https://cloud.ibm.com/registration.
2. Sign up with your email, verify it, and complete the profile.

Step 2: Log in to the IBM Quantum Platform
------------------------------------------

1. Go to https://quantum.cloud.ibm.com.
2. Log in with your IBMid or with a Google account.
3. In the header, check the **account switcher** and the **region switcher**.
   Make sure the account you just created is selected. Open Plan instances
   live in ``us-east``.

Step 3: Create an Open Plan instance
------------------------------------

An **instance** is what your jobs are billed and tracked against.

1. Open the **Instances** page (https://quantum.cloud.ibm.com/instances). From
   the dashboard you can reach it with *View all*.
2. Click **Create instance**.
3. Enter a name (for example ``qalgos``). Tags are optional.
4. Select the **Open Plan** as the pricing plan.
5. Review the QPUs available to the instance. The defaults are fine.
6. Leave the access group at its default unless you are sharing the instance
   with collaborators.
7. Click **Create instance**.

The new instance appears on the Instances page together with its **CRN**
(Cloud Resource Name), a long identifier that starts with ``crn:v1:``. You
will need it, or the instance name, in the next page.

.. seealso::

   Next: :doc:`credentials` shows how to create an API key and connect Qiskit
   to your instance.

.. _ibm-references:

References
----------

* `IBM Quantum Platform <https://quantum.cloud.ibm.com>`_
* `Plans overview
  <https://quantum.cloud.ibm.com/docs/en/guides/plans-overview>`_: Open Plan
  cost, usage limit and region.
* `Set up your IBM Cloud account
  <https://quantum.cloud.ibm.com/docs/en/guides/cloud-setup>`_
* `Create and manage instances
  <https://quantum.cloud.ibm.com/docs/en/guides/instances>`_
* `IBM Cloud registration <https://cloud.ibm.com/registration>`_
