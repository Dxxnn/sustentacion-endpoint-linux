# Sintesis academica del proyecto

Fuente principal revisada: `Grupo 6 revisado - Daniel Lopez CORREGIDO APA7.docx`.

Fuentes EAN revisadas:

- `5. Proyecto de grado - Metodologia - herramientas.pdf`
- `6. Proyecto de grado - Resultados.pdf`
- `7. Proyecto de grado - Divulgacion.pdf`
- `8. Proyecto de grado - Costos.pdf`
- `10. Proyecto de grado - Sustentacion.pdf`
- `Research_Product_Template (2).xlsx`
- `BLANK_PRISMA_2009_Flow_Diagram.doc`

## Titulo

Titulo actual:

> Comparacion entre deteccion basada en reglas y Machine Learning para la identificacion de cadenas de procesos sospechosas en endpoints Linux.

Titulo mejorado recomendado:

> Comparacion entre reglas tipo SIEM e Isolation Forest para detectar cadenas de procesos sospechosas en endpoints Linux instrumentados con auditd.

Motivo: conserva el alcance original, explicita el algoritmo inicial y deja claro que auditd es la fuente de telemetria.

## Pregunta de investigacion

¿Que diferencias de desempeño existen, en terminos de tasa de deteccion, tasa de falsos positivos y tiempo de deteccion, entre un enfoque basado en reglas tipo SIEM y un detector de anomalías basado en aprendizaje automatico para identificar relaciones padre-hijo inusuales y secuencias de descarga y ejecucion en un endpoint Linux instrumentado con auditd?

## Objetivo general

Comparar el desempeño de un enfoque basado en reglas tipo SIEM y de un detector de anomalías basado en aprendizaje automatico para identificar relaciones padre-hijo inusuales y secuencias de descarga y ejecucion en un endpoint Linux instrumentado con auditd.

## Objetivos especificos

1. Desarrollar un laboratorio local con un endpoint Linux, recoleccion de registros mediante auditd y un entorno de experimentacion controlado.
2. Construir escenarios reproducibles de actividad normal, relaciones padre-hijo sospechosas y secuencias de descarga y ejecucion inmediata.
3. Implementar reglas de deteccion tipo SIEM orientadas a los comportamientos definidos.
4. Entrenar un detector de anomalías con variables extraidas de los registros auditd.
5. Evaluar comparativamente ambos enfoques mediante tasa de deteccion, tasa de falsos positivos, precision, sensibilidad, F1 score y tiempo de deteccion.

## Metodologia

Enfoque cuantitativo, aplicado y experimental de laboratorio.

Etapas:

1. Preparacion del laboratorio: VM Linux, auditd, reglas de auditoria, reloj y verificacion de logs.
2. Generacion de actividad normal para linea base.
3. Ejecucion de escenarios controlados sospechosos, sin malware real.
4. Recoleccion y normalizacion de registros auditd.
5. Implementacion de dos detectores sobre el mismo corpus: reglas tipo SIEM e Isolation Forest.
6. Consolidacion de resultados en matrices de confusion, tablas comparativas y graficas.

## Variables

Variables independientes:

- Enfoque de deteccion: reglas tipo SIEM o detector de anomalías.
- Tipo de escenario: actividad normal, relacion padre-hijo inusual, descarga seguida de ejecucion.

Variables dependientes:

- Tasa de deteccion.
- Tasa de falsos positivos.
- Precision.
- Sensibilidad / recall.
- F1 score.
- Tiempo de deteccion.

Variables de control:

- Misma VM Linux.
- Mismas reglas auditd.
- Mismas ventanas temporales.
- Mismos escenarios y repeticiones.
- Misma fuente de logs.

## Metricas

- True positives, false positives, true negatives, false negatives.
- Detection rate / recall: `TP / (TP + FN)`.
- False positive rate: `FP / (FP + TN)`.
- Precision: `TP / (TP + FP)`.
- F1 score: `2 * precision * recall / (precision + recall)`.
- Tiempo de deteccion: diferencia entre inicio del evento y momento de alerta.
- Area bajo curva precision-recall si se usan puntajes continuos.

## Herramientas

- VM Linux validada: Ubuntu Server 24.04.4 LTS.
- auditd, auditctl, ausearch, aureport.
- Bash para escenarios controlados.
- Python para parsing, variables y comparacion.
- pandas, NumPy, scikit-learn.
- Isolation Forest como modelo inicial explicable.
- Jupyter Notebook para trazabilidad.
- Matplotlib o seaborn para graficas.
- Reglas tipo SIEM implementadas primero como script reproducible; opcionalmente portables a Wazuh, Elastic o Splunk.

## Restricciones

- No usar malware real.
- No atacar terceros.
- No usar payloads peligrosos.
- Laboratorio local aislado.
- Muestra compuesta por eventos tecnicos, no participantes humanos.
- Los resultados dependen de las repeticiones y de la calidad del etiquetado.
- auditd puede generar volumen alto de logs si las reglas son demasiado amplias.
- La VM debe mantener configuracion constante durante las pruebas.
- Las conclusiones aplican al laboratorio y no deben generalizarse sin validacion externa.

## Entregables esperados

- VM Linux instrumentada.
- Reglas auditd.
- Escenarios reproducibles.
- Logs crudos y procesados.
- Dataset con variables de comportamiento.
- Reglas tipo SIEM.
- Modelo Isolation Forest inicial.
- Tabla de metricas comparativas.
- Evidencia visual de avance.
- Presentacion de primera sustentacion.

## Criterios EAN relevantes para la sustentacion

Del PDF de sustentacion:

- Primera sustentacion: 10 minutos de presentacion y 5 minutos de preguntas.
- Capacidad de sintesis: solo lo relevante.
- No leer las diapositivas.
- Usar imagenes, palabras clave y diagramas sinteticos.
- Todas las diapositivas deben tener titulo.
- Estructura recomendada: introduccion, objetivos, pregunta problema, estado del arte, metodologia, resultados/avance, arquitectura, pruebas, costos y conclusiones.

Del PDF de metodologia:

- Alinear objetivo general, objetivos especificos y etapas.
- Definir restricciones tecnicas, economicas, legales, de seguridad y de disponibilidad.
- Describir variables e instrumentos con suficiente detalle para reproducibilidad.

Del PDF de resultados:

- Presentar hallazgos de forma objetiva.
- No manipular ni inventar resultados.
- Usar tablas y graficas para metodologia cuantitativa.
- Conectar objetivo especifico, metodologia y resultado.
