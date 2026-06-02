#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
cd "${ROOT_DIR}"

bash -n scripts/*.sh
"${PYTHON}" -m py_compile scripts/*.py
"${PYTHON}" -m unittest discover -s tests -v

echo "[checks] Validaciones completadas."

