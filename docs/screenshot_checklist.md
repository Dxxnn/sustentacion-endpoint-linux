# Checklist exacto de screenshots

Guarda las capturas en `screenshots/` con nombres numerados.

## 01 - VM creada

Captura la pantalla del hipervisor con:

- Nombre de la VM.
- Distribucion Linux.
- CPU/RAM/disco.
- Red NAT.

Nombre sugerido: `01_vm_config.png`.

## 02 - Version del sistema operativo

Comandos:

```bash
hostnamectl
cat /etc/os-release
uname -a
```

Nombre sugerido: `02_os_version.png`.

## 03 - Estado de auditd

Comandos:

```bash
sudo systemctl status auditd --no-pager
sudo auditctl -s
```

Nombre sugerido: `03_auditd_status.png`.

## 04 - Reglas auditctl activas

Comando:

```bash
sudo auditctl -l
```

Nombre sugerido: `04_audit_rules.png`.

## 05 - Ejecucion de escenarios

Comando:

```bash
./scripts/02_run_scenarios.sh
tail -n 10 data/raw/scenario_labels.csv
```

Nombre sugerido: `05_scenarios_execution.png`.

## 06 - Logs con ausearch

Comandos:

```bash
sudo ausearch -k project_exec -i | tail -n 40
sudo ausearch -k project_lab_dir -i | tail -n 40
```

Nombre sugerido: `06_ausearch_logs.png`.

## 07 - Reportes con aureport

Comandos:

```bash
sudo aureport -x --summary
sudo aureport -f -i
```

Nombre sugerido: `07_aureport_summary.png`.

## 08 - Dataset generado

Comandos:

```bash
python3 scripts/parse_audit_log.py --input data/raw/audit.log --output data/processed/audit_events.csv
head -n 20 data/processed/audit_events.csv
```

Nombre sugerido: `08_dataset_audit_events.png`.

## 09 - Variables construidas

Comandos:

```bash
python3 scripts/build_features.py --events data/processed/audit_events.csv --labels data/raw/scenario_labels.csv --output data/processed/features.csv
head -n 20 data/processed/features.csv
```

Nombre sugerido: `09_features_dataset.png`.

## 10 - Script o notebook de procesamiento

Abre:

- `notebooks/01_procesamiento_y_modelo.ipynb`, o
- `scripts/isolation_forest_baseline.py`.

Nombre sugerido: `10_notebook_or_script.png`.

## 11 - Primera comparacion

Comandos:

```bash
./scripts/run_pipeline.sh
cat results/rule_metrics.csv
cat results/isolation_forest_metrics.csv
```

Si aun no hay datos suficientes, muestra `results/metricas_esperadas.csv` y marca la diapositiva como "pendiente de validacion".

Nombre sugerido: `11_first_comparison.png`.

## 12 - Evidencia visual para diapositiva de avance

Combina en una sola captura o collage:

- `auditctl -l`
- salida de `ausearch`
- `head data/processed/features.csv`

Nombre sugerido: `12_technical_progress_collage.png`.
