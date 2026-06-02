# Guia tecnica del laboratorio

## Proposito

Montar un endpoint Linux controlado para comparar dos enfoques de deteccion:

- Reglas explicitas tipo SIEM.
- Deteccion de anomalías con Isolation Forest.

La misma telemetria auditd alimenta ambos enfoques para que la comparacion sea justa.

## Arquitectura logica

```text
VM Linux
  |
  |-- auditd + reglas auditctl
  |      |
  |      +-- /var/log/audit/audit.log
  |
  |-- escenarios controlados
  |      |-- actividad normal
  |      |-- padre-hijo inusual
  |      +-- descarga local + chmod + ejecucion
  |
  +-- pipeline Python
         |-- parse_audit_log.py
         |-- build_features.py
         |-- rule_detector.py
         +-- isolation_forest_baseline.py
```

## Instalacion base

```bash
sudo apt update
sudo apt install -y auditd audispd-plugins curl wget python3 python3-venv python3-pip
sudo systemctl enable --now auditd
sudo systemctl status auditd --no-pager
```

## Reglas auditd activas

Se aplican con:

```bash
./scripts/01_apply_audit_rules.sh
```

Verificacion:

```bash
sudo auditctl -s
sudo auditctl -l
```

Reglas principales:

- `execve`: ejecucion de procesos.
- `chmod/fchmod/fchmodat`: cambios de permisos.
- watch sobre `/tmp/project_audit_lab`: escritura, lectura, atributos y ejecucion.

## Escenarios seguros

Escenario normal:

- Comandos basicos del sistema.
- Lectura de `/etc/os-release`.
- Creacion de archivos temporales benignos.
- Ejecucion de Python que imprime texto.

Relacion padre-hijo inusual:

- `python3 -> sh`.
- `awk -> sh`.
- `find -> sh`.

Secuencia benigna de descarga y ejecucion:

- Servidor local en `127.0.0.1`.
- Descarga de `hello.sh` con `curl` o `wget`.
- `chmod +x`.
- Ejecucion del script inocuo.

## Recoleccion

```bash
./scripts/03_collect_audit_logs.sh
```

Salidas esperadas:

- `data/raw/audit.log`
- `data/raw/ausearch_project_exec.txt`
- `data/raw/ausearch_project_lab_dir.txt`
- `data/raw/aureport_exec_summary.txt`
- `data/raw/aureport_file_summary.txt`
- `data/raw/scenario_labels.csv`

## Procesamiento

```bash
./scripts/run_pipeline.sh
```

Salidas esperadas:

- `data/processed/audit_events.csv`
- `data/processed/features.csv`
- `results/rule_detections.csv`
- `results/rule_metrics.csv`
- `results/isolation_forest_scores.csv`
- `results/isolation_forest_metrics.csv`
- `results/models/isolation_forest_pipeline.joblib`

Verificacion del modelo:

```bash
.venv/bin/python scripts/verify_model.py
```

## Interpretacion para primera sustentacion

Si aun no se han ejecutado repeticiones completas:

- Presentar como avance: VM, auditd, reglas, escenarios, logs y dataset.
- Presentar metricas como definiciones y plan de evaluacion.
- No afirmar que ML supera reglas o viceversa.
- Mostrar una tabla con columnas "pendiente de validacion".
