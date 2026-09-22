C++ setup (Armadillo)
=====================

The C++ track uses `Armadillo <https://arma.sourceforge.net/>`_ for linear
algebra and `yaml-cpp <https://github.com/jbeder/yaml-cpp>`_ to read the same
YAML inputs as the Python track. The compiler, CMake, Armadillo and yaml-cpp
all come from the conda environment, so there is nothing extra to install:

.. code-block:: bash

   ./install.sh
   conda activate qalgos

If you already did the :doc:`python` setup, you are done.

Building a program
------------------

Layout:

.. code-block:: text

   cpp/
   ├── CMakeLists.txt
   └── main.cpp

``cpp/CMakeLists.txt``:

.. code-block:: cmake

   cmake_minimum_required(VERSION 3.16)
   project(qalgos CXX)

   set(CMAKE_CXX_STANDARD 17)
   set(CMAKE_CXX_STANDARD_REQUIRED ON)
   if(NOT CMAKE_BUILD_TYPE)
     set(CMAKE_BUILD_TYPE Release)
   endif()

   find_package(Armadillo REQUIRED)
   find_package(yaml-cpp REQUIRED)

   add_executable(app main.cpp)
   target_include_directories(app PRIVATE ${ARMADILLO_INCLUDE_DIRS})
   target_link_libraries(app PRIVATE ${ARMADILLO_LIBRARIES} yaml-cpp::yaml-cpp)

Build and run, with the environment active:

.. code-block:: bash

   cmake -S cpp -B build -G Ninja -DCMAKE_PREFIX_PATH="$CONDA_PREFIX"
   cmake --build build
   ./build/app configs/example.yaml

Quick check without CMake
-------------------------

.. code-block:: bash

   c++ -std=c++17 -O2 main.cpp -o app \
       -I"$CONDA_PREFIX/include" -L"$CONDA_PREFIX/lib" \
       -larmadillo -lyaml-cpp -Wl,-rpath,"$CONDA_PREFIX/lib"

Tips
----

* Build in ``Release`` mode. Armadillo is much slower without optimization.
* Armadillo uses BLAS and LAPACK underneath. The conda package links against
  an optimized one, so large matrix operations are fast.
* Complex amplitudes: use ``arma::cx_vec`` and ``arma::cx_mat``.
* Large sparse operators (Hamiltonians): use ``arma::sp_mat``.
* Read all experiment parameters from YAML rather than hard-coding them. See
  the example on :doc:`the configuration page </concepts/configuration>`.
