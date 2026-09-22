#!/usr/bin/env bash
# Build the Qiskit C library and fetch the Qiskit C++ headers into third_party/.
# Needs the `qalgos` environment active (it provides Rust and CMake).
#
# Usage:  conda activate qalgos && ./scripts/install_qiskit_cpp.sh
set -euo pipefail

QISKIT_REF="${QISKIT_REF:-2.5.2}"     # Qiskit release to build (C API needs >= 2.2)
QISKIT_CPP_REF="${QISKIT_CPP_REF:-main}"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TP="$REPO_DIR/third_party"

log() { printf '\n==> %s\n' "$*"; }

command -v cargo >/dev/null 2>&1 || {
  echo "cargo not found. Activate the environment first: conda activate qalgos" >&2
  exit 1
}

mkdir -p "$TP"

fetch() {  # fetch <url> <dir> <ref>
  if [ -d "$2/.git" ]; then
    git -C "$2" fetch -q --depth 1 origin "$3"
    git -C "$2" -c advice.detachedHead=false checkout -q FETCH_HEAD
  else
    git -c advice.detachedHead=false clone -q --depth 1 --branch "$3" "$1" "$2"
  fi
}

log "Fetching Qiskit $QISKIT_REF"
fetch https://github.com/Qiskit/qiskit.git "$TP/qiskit" "$QISKIT_REF"

log "Fetching Qiskit C++ ($QISKIT_CPP_REF)"
fetch https://github.com/Qiskit/qiskit-cpp.git "$TP/qiskit-cpp" "$QISKIT_CPP_REF"

log "Building the Qiskit C library (first build takes several minutes)"
make -C "$TP/qiskit" c

test -d "$TP/qiskit/dist/c/include" && test -d "$TP/qiskit/dist/c/lib" \
  || { echo "Qiskit C build produced no dist/c output" >&2; exit 1; }

log "Done."
echo "  QISKIT_ROOT     = $TP/qiskit"
echo "  QISKIT_CPP_ROOT = $TP/qiskit-cpp"
