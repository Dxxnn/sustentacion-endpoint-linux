# Primera sustentacion - deteccion en endpoints Linux

Proyecto base para preparar la primera sustentacion de proyecto de grado en Ingenieria de Sistemas, Universidad EAN.

Tema de trabajo:

> Comparacion entre deteccion basada en reglas y Machine Learning para la identificacion de cadenas de procesos sospechosas en endpoints Linux.

Este paquete separa lo academico de lo tecnico:

- `docs/`: sintesis del documento, estructura de presentacion, checklist de capturas y guia tecnica.
- `slides/`: borrador de presentacion en Markdown exportable a PPTX.
- `screenshots/`: espacio para evidencias visuales de la VM, auditd, logs y resultados.
- `scripts/`: instalacion/configuracion de auditd, escenarios seguros, parsing, reglas y ML.
- `data/raw/`: logs crudos, salidas de `ausearch`, `aureport` y etiquetas de escenarios.
- `data/processed/`: datasets derivados y matriz de variables.
- `notebooks/`: notebook guia o instrucciones de ejecucion analitica.
- `results/`: detecciones, metricas y tablas comparativas.

## Estado actual

El laboratorio cuenta con una validacion controlada ejecutada el 2 de junio de
2026. Se procesaron 35787 eventos auditd: 34364 normales etiquetados, 319
sospechosos etiquetados y 1104 sin etiqueta. El detalle metodologico y las
metricas se encuentran en
[`docs/controlled_validation_2026-06-02.md`](docs/controlled_validation_2026-06-02.md).

Los resultados corresponden a un laboratorio reproducible. No equivalen a una
validacion en produccion.

## VM Linux recomendada

Para la sustentacion, usa una VM local aislada. Recomendacion conservadora:

- Ubuntu Server 24.04.4 LTS, que corresponde al entorno usado para la validacion
  controlada incluida en este repositorio.

Configuracion sugerida:

- 2 vCPU.
- 4 GB RAM minimo.
- 25 GB disco.
- Red NAT.
- Sin datos personales ni credenciales reales.
- Snapshot antes de instalar auditd y antes de cada tanda de pruebas.

## Preparacion rapida en la VM

Clona o copia esta carpeta dentro de la VM y ejecuta desde la raiz del paquete:

```bash
cd sustentacion_endpoint_linux
chmod +x scripts/*.sh
./scripts/00_setup_auditd.sh
./scripts/01_apply_audit_rules.sh
sudo auditctl -s
sudo auditctl -l
```

Genera eventos seguros:

```bash
./scripts/02_run_scenarios.sh
./scripts/03_collect_audit_logs.sh
```

Crea datasets y detectores iniciales:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
./scripts/run_pipeline.sh
```

Verifica el modelo entrenado con un comando corto:

```bash
.venv/bin/python scripts/verify_model.py
```

Ejecuta las pruebas automatizadas:

```bash
PYTHON=.venv/bin/python ./scripts/run_checks.sh
```

## Comandos clave para evidencia

```bash
hostnamectl
cat /etc/os-release
sudo systemctl status auditd --no-pager
sudo auditctl -s
sudo auditctl -l
sudo ausearch -k project_exec -i | tail -n 40
sudo ausearch -k project_lab_dir -i | tail -n 40
sudo aureport -x --summary
sudo aureport -f -i
```

Guarda capturas en `screenshots/` siguiendo `docs/screenshot_checklist.md`.

## Flujo reproducible

1. Configurar VM Linux y auditd.
2. Activar reglas de auditoria.
3. Ejecutar escenarios benignos/controlados.
4. Recolectar logs crudos.
5. Parsear logs a CSV.
6. Construir variables de comportamiento.
7. Aplicar reglas tipo SIEM.
8. Entrenar/evaluar Isolation Forest.
9. Comparar tasa de deteccion, falsos positivos, precision, recall, F1 y tiempo de deteccion.

## Seguridad del laboratorio

Los escenarios incluidos no usan malware, no atacan terceros y no descargan payloads externos. La secuencia de descarga usa un servidor local en `127.0.0.1` que entrega un script inocuo que solo imprime texto y crea archivos temporales.

## Entregables esperados

- Laboratorio Linux instrumentado con auditd.
- Reglas auditd y reglas tipo SIEM documentadas.
- Dataset de eventos de auditoria.
- Variables de comportamiento por evento.
- Detector de reglas.
- Detector de anomalías con Isolation Forest.
- Script reutilizable para verificar el modelo entrenado.
- Tabla comparativa de metricas.
- Evidencia visual para la sustentacion.
- Presentacion de 10 minutos.
