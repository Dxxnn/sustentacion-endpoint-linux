# Validacion controlada del laboratorio

Fecha de ejecucion: 2026-06-02.

## Alcance

La corrida se ejecuto en una VM Ubuntu Server 24.04.4 LTS instrumentada con
`auditd`. Los escenarios son inocuos y controlados: actividad normal, cadenas
padre-hijo inusuales y descarga local desde `127.0.0.1` seguida de ejecucion.

## Dataset

| Categoria | Eventos |
| --- | ---: |
| Eventos auditd procesados | 35787 |
| Normales etiquetados | 34364 |
| Sospechosos etiquetados | 319 |
| Sin etiqueta | 1104 |

## Detector de reglas

| Metrica | Valor |
| --- | ---: |
| Precision | 1.0000 |
| Recall | 0.7273 |
| Tasa de falsos positivos | 0.0000 |
| F1 | 0.8421 |
| Ventanas sospechosas detectadas | 16/16 |
| Ventanas normales con alerta | 0/4 |

## Isolation Forest

El modelo se entreno exclusivamente con eventos normales etiquetados. Para la
comparacion principal se uso `contamination=0.05`, el valor con mejor F1 entre
los umbrales explorados: `0.02`, `0.05`, `0.10` y `0.15`.

| Metrica | Valor |
| --- | ---: |
| Precision | 0.0824 |
| Recall | 0.4671 |
| Tasa de falsos positivos | 0.0483 |
| F1 | 0.1400 |
| Ventanas sospechosas detectadas | 16/16 |
| Ventanas normales con alerta | 4/4 |

## Interpretacion

Las reglas presentan mejor desempeno para los patrones conocidos del
laboratorio. Isolation Forest conserva valor como linea base complementaria,
pero genera alertas en las cuatro ventanas normales retenidas y requiere mayor
diversidad de actividad legitima, calibracion y validacion externa antes de
considerar un uso productivo.

El recolector concatena `audit.log` y sus rotaciones disponibles antes del
procesamiento. Esto evita perder ventanas tempranas cuando `auditd` rota el log
durante una tanda extensa.

Las metricas son evidencia controlada del prototipo. No equivalen a una
evaluacion en produccion.
