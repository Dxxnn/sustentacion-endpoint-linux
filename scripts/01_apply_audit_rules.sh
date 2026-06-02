#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

LAB_DIR="${LAB_DIR:-/tmp/project_audit_lab}"
RULES_FILE="/etc/audit/rules.d/project_endpoint.rules"

echo "[audit-rules] Preparando directorio de laboratorio: ${LAB_DIR}"
mkdir -p "${LAB_DIR}"
chmod 755 "${LAB_DIR}"

echo "[audit-rules] Limpiando reglas activas temporales..."
${SUDO} auditctl -D || true

echo "[audit-rules] Cargando reglas temporales con auditctl..."
${SUDO} auditctl -a always,exit -F arch=b64 -S execve -k project_exec
${SUDO} auditctl -a always,exit -F arch=b32 -S execve -k project_exec || true
${SUDO} auditctl -a always,exit -F arch=b64 -S chmod -S fchmod -S fchmodat -k project_perm_change
${SUDO} auditctl -a always,exit -F arch=b32 -S chmod -S fchmod -S fchmodat -k project_perm_change || true
${SUDO} auditctl -w "${LAB_DIR}" -p warx -k project_lab_dir

echo "[audit-rules] Escribiendo reglas persistentes en ${RULES_FILE}..."
tmp_rules="$(mktemp)"
cat > "${tmp_rules}" <<EOF
# Reglas para proyecto de grado: endpoint Linux + auditd
# Captura ejecucion de procesos, cambios de permisos y actividad del laboratorio.
-D
-a always,exit -F arch=b64 -S execve -k project_exec
-a always,exit -F arch=b32 -S execve -k project_exec
-a always,exit -F arch=b64 -S chmod -S fchmod -S fchmodat -k project_perm_change
-a always,exit -F arch=b32 -S chmod -S fchmod -S fchmodat -k project_perm_change
-w ${LAB_DIR} -p warx -k project_lab_dir
EOF

${SUDO} install -m 0640 "${tmp_rules}" "${RULES_FILE}"
rm -f "${tmp_rules}"

if command -v augenrules >/dev/null 2>&1; then
  echo "[audit-rules] Compilando reglas persistentes con augenrules..."
  ${SUDO} augenrules --load || true
fi

echo "[audit-rules] Estado auditd:"
${SUDO} auditctl -s

echo "[audit-rules] Reglas activas:"
${SUDO} auditctl -l
