#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "[setup] Detectando distribucion Linux..."
if [[ -f /etc/os-release ]]; then
  . /etc/os-release
  DISTRO_ID="${ID:-unknown}"
else
  DISTRO_ID="unknown"
fi

echo "[setup] Distribucion: ${DISTRO_ID}"

case "${DISTRO_ID}" in
  ubuntu|debian)
    ${SUDO} apt update
    ${SUDO} apt install -y auditd audispd-plugins curl wget python3 python3-venv python3-pip
    ;;
  fedora)
    ${SUDO} dnf install -y audit audit-libs curl wget python3 python3-pip
    ;;
  rhel|centos|rocky|almalinux)
    ${SUDO} dnf install -y audit audit-libs curl wget python3 python3-pip
    ;;
  *)
    echo "[setup] Distribucion no reconocida. Instala manualmente: auditd/audit, curl, wget, python3."
    ;;
esac

echo "[setup] Habilitando auditd..."
${SUDO} systemctl enable --now auditd
${SUDO} systemctl status auditd --no-pager || true

echo "[setup] Versiones de referencia:"
uname -a
python3 --version
auditctl -v || true

echo "[setup] Listo. Ejecuta scripts/01_apply_audit_rules.sh para cargar reglas."
