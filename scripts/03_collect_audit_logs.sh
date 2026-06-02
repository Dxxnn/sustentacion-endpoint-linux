#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="${ROOT_DIR}/data/raw"

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

mkdir -p "${RAW_DIR}"

echo "[collect] Copiando audit.log crudo y rotaciones disponibles..."
mapfile -t audit_logs < <(find /var/log/audit -maxdepth 1 -type f -name 'audit.log*' -print | sort -V -r)
if [[ "${#audit_logs[@]}" -eq 0 ]]; then
  echo "No se encontraron archivos audit.log." >&2
  exit 1
fi
${SUDO} cat "${audit_logs[@]}" > "${RAW_DIR}/audit.log"
echo "[collect] Archivos concatenados: ${audit_logs[*]}"

echo "[collect] Generando salidas ausearch..."
${SUDO} ausearch -k project_exec -i > "${RAW_DIR}/ausearch_project_exec.txt" || true
${SUDO} ausearch -k project_perm_change -i > "${RAW_DIR}/ausearch_project_perm_change.txt" || true
${SUDO} ausearch -k project_lab_dir -i > "${RAW_DIR}/ausearch_project_lab_dir.txt" || true

echo "[collect] Generando reportes aureport..."
${SUDO} aureport -x --summary > "${RAW_DIR}/aureport_exec_summary.txt" || true
${SUDO} aureport -f -i > "${RAW_DIR}/aureport_file_summary.txt" || true
${SUDO} aureport --summary > "${RAW_DIR}/aureport_summary.txt" || true

echo "[collect] Archivos generados:"
find "${RAW_DIR}" -maxdepth 1 -type f -print | sort
