#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAB_DIR="${LAB_DIR:-/tmp/project_audit_lab}"
RAW_DIR="${ROOT_DIR}/data/raw"
LABELS="${RAW_DIR}/scenario_labels.csv"
NORMAL_ITERATIONS="${NORMAL_ITERATIONS:-20}"
RUN_MODE="${RUN_MODE:-all}"
SCENARIO_GAP_SECONDS="${SCENARIO_GAP_SECONDS:-2}"

mkdir -p "${LAB_DIR}" "${RAW_DIR}"

if [[ ! "${NORMAL_ITERATIONS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "NORMAL_ITERATIONS debe ser un entero positivo." >&2
  exit 1
fi

if [[ ! -f "${LABELS}" ]]; then
  echo "run_id,scenario,expected_label,start_time_utc,end_time_utc,description" > "${LABELS}"
fi

new_run_id() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr '[:upper:]' '[:lower:]'
  else
    date -u +"run-%Y%m%d%H%M%S"
  fi
}

record_scenario() {
  local scenario="$1"
  local expected_label="$2"
  local description="$3"
  local run_id
  local start_ts
  local end_ts

  run_id="$(new_run_id)"
  start_ts="$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")"
  echo "[scenario] Inicio ${scenario} (${run_id})"

  case "${scenario}" in
    normal_activity)
      run_normal_activity
      ;;
    unusual_parent_child)
      run_unusual_parent_child
      ;;
    benign_download_execute)
      run_benign_download_execute
      ;;
    *)
      echo "Escenario desconocido: ${scenario}" >&2
      exit 1
      ;;
  esac

  end_ts="$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")"
  printf '%s,%s,%s,%s,%s,"%s"\n' "${run_id}" "${scenario}" "${expected_label}" "${start_ts}" "${end_ts}" "${description}" >> "${LABELS}"
  echo "[scenario] Fin ${scenario}"
}

run_normal_activity() {
  mkdir -p "${LAB_DIR}/normal"
  for idx in $(seq 1 "${NORMAL_ITERATIONS}"); do
    date > "${LAB_DIR}/normal/date_${idx}.txt"
    whoami > "${LAB_DIR}/normal/user_${idx}.txt"
    uname -a > "${LAB_DIR}/normal/uname_${idx}.txt"
    cp /etc/os-release "${LAB_DIR}/normal/os-release_${idx}.copy"
    ls -la "${LAB_DIR}/normal" >/dev/null
    python3 -c 'print("calculo benigno de laboratorio")' > "${LAB_DIR}/normal/python_output_${idx}.txt"
    /bin/echo "actividad normal completada" >> "${LAB_DIR}/normal/normal.txt"
    sleep 1
  done
}

run_unusual_parent_child() {
  mkdir -p "${LAB_DIR}/unusual"
  python3 -c 'import subprocess, pathlib; p=pathlib.Path("/tmp/project_audit_lab/unusual/python_child.txt"); p.parent.mkdir(parents=True, exist_ok=True); subprocess.run(["/bin/sh","-c",f"echo python_spawn_shell > {p}"], check=True)'
  awk 'BEGIN { system("/bin/sh -c \"echo awk_spawn_shell > /tmp/project_audit_lab/unusual/awk_child.txt\"") }'
  touch "${LAB_DIR}/unusual/find_source.txt"
  find "${LAB_DIR}/unusual" -maxdepth 1 -name "find_source.txt" -exec /bin/sh -c 'echo find_spawn_shell > /tmp/project_audit_lab/unusual/find_child.txt' \;
}

run_benign_download_execute() {
  local server_dir="${LAB_DIR}/server"
  local download_dir="${LAB_DIR}/downloaded"
  local server_pid=""

  mkdir -p "${server_dir}" "${download_dir}"
  cat > "${server_dir}/hello.sh" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
echo "script inocuo ejecutado"
echo "hello from local lab" > /tmp/project_audit_lab/downloaded/execution_marker.txt
EOS

  python3 -m http.server 8765 --bind 127.0.0.1 --directory "${server_dir}" > "${LAB_DIR}/http_server.log" 2>&1 &
  server_pid="$!"
  trap '[[ -n "${server_pid:-}" ]] && kill "${server_pid}" >/dev/null 2>&1 || true' RETURN
  sleep 1

  if command -v curl >/dev/null 2>&1; then
    curl -fsS "http://127.0.0.1:8765/hello.sh" -o "${download_dir}/hello.sh"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "http://127.0.0.1:8765/hello.sh" -O "${download_dir}/hello.sh"
  else
    echo "Se requiere curl o wget para este escenario." >&2
    return 1
  fi

  chmod +x "${download_dir}/hello.sh"
  "${download_dir}/hello.sh" > "${download_dir}/hello_output.txt"
  kill "${server_pid}" >/dev/null 2>&1 || true
  server_pid=""
  trap - RETURN
}

case "${RUN_MODE}" in
  normal)
    record_scenario "normal_activity" "normal" "Comandos administrativos benignos y archivos temporales"
    ;;
  suspicious)
    record_scenario "unusual_parent_child" "suspicious" "Procesos python/awk/find invocan shell para crear archivos inocuos"
    sleep "${SCENARIO_GAP_SECONDS}"
    record_scenario "benign_download_execute" "suspicious" "Descarga local desde 127.0.0.1 seguida de chmod y ejecucion inocua"
    ;;
  all)
    record_scenario "normal_activity" "normal" "Comandos administrativos benignos y archivos temporales"
    sleep "${SCENARIO_GAP_SECONDS}"
    record_scenario "unusual_parent_child" "suspicious" "Procesos python/awk/find invocan shell para crear archivos inocuos"
    sleep "${SCENARIO_GAP_SECONDS}"
    record_scenario "benign_download_execute" "suspicious" "Descarga local desde 127.0.0.1 seguida de chmod y ejecucion inocua"
    ;;
  *)
    echo "RUN_MODE debe ser normal, suspicious o all." >&2
    exit 1
    ;;
esac

echo "[scenario] Etiquetas actualizadas en ${LABELS}"
tail -n 5 "${LABELS}"
