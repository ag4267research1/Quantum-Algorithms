#!/usr/bin/env bash
# One-shot setup: Miniconda (if missing) + the `qalgos` environment
# (Python, Qiskit, C++ toolchain, Armadillo, yaml-cpp).
#
# Usage:  ./install.sh
# Works on macOS and Linux. On Windows, use WSL2.
set -euo pipefail

ENV_NAME="qalgos"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MINICONDA_DIR="${MINICONDA_DIR:-$HOME/miniconda3}"

log() { printf '\n==> %s\n' "$*"; }

install_miniconda() {
  local os arch installer
  os="$(uname -s)"
  arch="$(uname -m)"
  case "$os-$arch" in
    Darwin-arm64)   installer="Miniconda3-latest-MacOSX-arm64.sh" ;;
    Darwin-x86_64)  installer="Miniconda3-latest-MacOSX-x86_64.sh" ;;
    Linux-x86_64)   installer="Miniconda3-latest-Linux-x86_64.sh" ;;
    Linux-aarch64)  installer="Miniconda3-latest-Linux-aarch64.sh" ;;
    *) echo "Unsupported platform: $os-$arch (on Windows, use WSL2)" >&2; exit 1 ;;
  esac

  log "Downloading Miniconda ($installer)"
  local tmp
  tmp="$(mktemp -d)"
  curl -fsSL "https://repo.anaconda.com/miniconda/$installer" -o "$tmp/miniconda.sh"

  log "Installing Miniconda to $MINICONDA_DIR"
  bash "$tmp/miniconda.sh" -b -p "$MINICONDA_DIR"
  rm -rf "$tmp"
}

# 1. Miniconda
if command -v conda >/dev/null 2>&1; then
  CONDA_BASE="$(conda info --base)"
  log "Found conda at $CONDA_BASE"
elif [ -x "$MINICONDA_DIR/bin/conda" ]; then
  CONDA_BASE="$MINICONDA_DIR"
  log "Found Miniconda at $CONDA_BASE"
else
  install_miniconda
  CONDA_BASE="$MINICONDA_DIR"
fi

# shellcheck disable=SC1091
source "$CONDA_BASE/etc/profile.d/conda.sh"

# 2. Environment
if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  log "Updating existing environment '$ENV_NAME'"
  conda env update -n "$ENV_NAME" -f "$REPO_DIR/environment.yml" --prune
else
  log "Creating environment '$ENV_NAME'"
  conda env create -f "$REPO_DIR/environment.yml"
fi

# 3. Verify
log "Verifying the installation"
conda run -n "$ENV_NAME" python - <<'EOF'
import qiskit, qiskit_aer, yaml, numpy, scipy
print("qiskit     ", qiskit.__version__)
print("qiskit-aer ", qiskit_aer.__version__)
print("pyyaml     ", yaml.__version__)
print("numpy      ", numpy.__version__)
print("scipy      ", scipy.__version__)
EOF

conda run -n "$ENV_NAME" bash -c '
  test -f "$CONDA_PREFIX/include/armadillo" && echo "armadillo   found" || { echo "armadillo missing"; exit 1; }
  test -d "$CONDA_PREFIX/include/yaml-cpp" && echo "yaml-cpp    found" || { echo "yaml-cpp missing"; exit 1; }
  c++ --version | head -1
  cmake --version | head -1
'

# 4. Make conda available in future shells
if ! command -v conda >/dev/null 2>&1; then
  log "Enabling conda in your shell (run once, then restart the terminal)"
  "$CONDA_BASE/bin/conda" init "$(basename "${SHELL:-bash}")" || true
fi

log "Done. Activate the environment with:  conda activate $ENV_NAME"
