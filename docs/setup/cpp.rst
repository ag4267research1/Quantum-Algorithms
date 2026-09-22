C++ setup (Qiskit C++ and Armadillo)
====================================

The C++ track mirrors the Python one:

* `Qiskit C++ <https://github.com/Qiskit/qiskit-cpp>`_ builds and transpiles
  quantum circuits, and submits them to a backend. It is a header-only layer
  over the Qiskit C library.
* `Armadillo <https://arma.sourceforge.net/>`_ does the linear algebra:
  state vectors, unitaries, Hamiltonians, eigenvalues, and the classical
  baselines.
* `yaml-cpp <https://github.com/jbeder/yaml-cpp>`_ reads the same YAML inputs
  as the Python track.

The compiler, CMake, Armadillo, yaml-cpp and Rust (needed once, to build the
Qiskit C library) all come from the conda environment:

.. code-block:: bash

   ./install.sh
   conda activate qalgos

If you already did the :doc:`python` setup, you only need the next step.

Installing Qiskit C++
---------------------

Qiskit C++ is not on conda or PyPI. It is a set of headers that call the
Qiskit C library, which is built from the Qiskit source. One script does both,
into ``third_party/`` (not committed):

.. code-block:: bash

   conda activate qalgos
   ./scripts/install_qiskit_cpp.sh

The first run compiles Qiskit's Rust code and takes several minutes. It needs
Qiskit 2.2 or newer; the script builds release ``2.5.2`` by default. To pick
another release:

.. code-block:: bash

   QISKIT_REF=2.5.2 ./scripts/install_qiskit_cpp.sh

What Qiskit C++ can and cannot do
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Circuit construction, parameters, observables and the transpiler run locally.
Running a circuit needs a backend interface (IBM Quantum through
``qiskit-ibm-runtime`` C, QRMI, or SQC), because Qiskit C++ has no built-in
simulator. For simulation in C++, use Armadillo: write the state vector and
gates as ``arma::cx_vec`` and ``arma::cx_mat``. This is also what serves as
the classical baseline.

Building a program
------------------

Layout:

.. code-block:: text

   cpp/
   ├── CMakeLists.txt
   └── main.cpp

``cpp/main.cpp`` (Qiskit builds the circuit, Armadillo holds the state):

.. code-block:: cpp

   #include <armadillo>
   #include <iostream>
   #include "circuit/quantumcircuit.hpp"

   using namespace Qiskit::circuit;

   int main() {
       QuantumRegister qr(2);
       ClassicalRegister cr(2);
       QuantumCircuit circ(qr, cr);
       circ.h(0);
       circ.cx(0, 1);
       circ.measure(0, 0);
       circ.measure(1, 1);
       std::cout << "qubits = " << circ.num_qubits() << "\n";

       arma::cx_vec psi = arma::randu<arma::cx_vec>(4);
       psi /= arma::norm(psi);
       std::cout << "norm   = " << arma::norm(psi) << "\n";
   }

``cpp/CMakeLists.txt``:

.. code-block:: cmake

   cmake_minimum_required(VERSION 3.16)
   project(qalgos CXX)

   set(CMAKE_CXX_STANDARD 17)
   set(CMAKE_CXX_STANDARD_REQUIRED ON)
   if(NOT CMAKE_BUILD_TYPE)
     set(CMAKE_BUILD_TYPE Release)
   endif()

   # Built by scripts/install_qiskit_cpp.sh
   set(TP ${CMAKE_SOURCE_DIR}/../third_party)
   set(QISKIT_LIB_DIR ${TP}/qiskit/dist/c/lib)

   find_package(Armadillo REQUIRED)
   find_package(yaml-cpp REQUIRED)

   add_executable(app main.cpp)
   target_include_directories(app PRIVATE
     ${TP}/qiskit-cpp/src
     ${TP}/qiskit/dist/c/include
     ${ARMADILLO_INCLUDE_DIRS})
   target_link_directories(app PRIVATE ${QISKIT_LIB_DIR})
   target_link_libraries(app PRIVATE
     qiskit ${ARMADILLO_LIBRARIES} yaml-cpp::yaml-cpp)
   set_target_properties(app PROPERTIES BUILD_RPATH ${QISKIT_LIB_DIR})

Build and run, with the environment active:

.. code-block:: bash

   cmake -S cpp -B build -G Ninja -DCMAKE_PREFIX_PATH="$CONDA_PREFIX"
   cmake --build build
   ./build/app configs/example.yaml

Quick check without CMake
-------------------------

.. code-block:: bash

   c++ -std=c++17 -O2 main.cpp -o app \
       -I third_party/qiskit-cpp/src -I third_party/qiskit/dist/c/include \
       -I"$CONDA_PREFIX/include" -L"$CONDA_PREFIX/lib" \
       -L third_party/qiskit/dist/c/lib -lqiskit -larmadillo -lyaml-cpp \
       -Wl,-rpath,"$PWD/third_party/qiskit/dist/c/lib" \
       -Wl,-rpath,"$CONDA_PREFIX/lib"

Tips
----

* Build in ``Release`` mode. Armadillo is much slower without optimization.
* Armadillo uses BLAS and LAPACK underneath. The conda package links against
  an optimized one, so large matrix operations are fast.
* Complex amplitudes: use ``arma::cx_vec`` and ``arma::cx_mat``.
* Large sparse operators (Hamiltonians): use ``arma::sp_mat``.
* Read all experiment parameters from YAML rather than hard-coding them. See
  the example on :doc:`the configuration page </concepts/configuration>`.
