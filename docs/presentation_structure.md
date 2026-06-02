# Estructura propuesta de presentacion

Duracion maxima: 10 minutos. Recomendacion: 10 diapositivas, 45 a 60 segundos por diapositiva.

## 1. Portada

Contenido maximo:

- Titulo del proyecto.
- Autor, programa, Universidad EAN.
- Directora y fecha.

Idea visual:

- Fondo blanco, franja verde EAN, acento naranja.
- Iconos discretos: endpoint, logs, ML.

Guion oral:

> Buenos dias. Mi proyecto compara dos formas de detectar actividad sospechosa en endpoints Linux: reglas tipo SIEM y un detector de anomalías con Machine Learning. La idea no es asumir que un enfoque es mejor, sino medirlos bajo el mismo laboratorio, con la misma telemetria y con escenarios reproducibles.

## 2. Contexto y problema

Contenido maximo:

- SOC: L1, L2, L3.
- Alertas SIEM/EDR.
- Falsos positivos = tiempo y ruido operativo.
- Problema: distinguir secuencias legitimas vs sospechosas.

Idea visual:

- Mini flujo: telemetria -> alerta -> analista -> decision.

Guion oral:

> En un SOC, los analistas reciben alertas de SIEM, EDR y otras fuentes. Muchas parecen peligrosas, pero terminan siendo actividad legitima. Cada falso positivo consume tiempo y puede activar respuestas innecesarias. El reto no es solo tener datos, sino diferenciar una secuencia normal de una realmente sospechosa.

## 3. Pregunta y objetivos

Contenido maximo:

- Pregunta en una frase.
- Objetivo general.
- Cinco objetivos especificos abreviados: laboratorio, escenarios, reglas, ML, evaluacion.

Idea visual:

- Cadena: pregunta -> objetivo -> evaluacion.

Guion oral:

> La pregunta es que diferencias de desempeño existen entre reglas tipo SIEM y un detector de anomalías para identificar relaciones padre-hijo inusuales y descarga seguida de ejecucion. El objetivo general es comparar ambos enfoques en las mismas condiciones, usando auditd y metricas homogeneas.

## 4. Estado del arte sintetizado

Contenido maximo:

- Reglas: interpretables, pero rigidas.
- ML: flexible, pero puede generar falsos positivos.
- Logs modernos: importan representacion y contexto.
- Brecha: comparacion directa en Linux con auditd.

Idea visual:

- Tabla 3 columnas: enfoque, aporte, limitacion.

Guion oral:

> La literatura muestra que las reglas siguen siendo valiosas por su explicabilidad, pero dependen de patrones conocidos. Los modelos de anomalías pueden adaptarse mejor, aunque requieren buena representacion de eventos y control de ruido. La brecha especifica es comparar ambos enfoques sobre procesos Linux auditados en un laboratorio controlado.

## 5. Metodologia y diseno experimental

Contenido maximo:

- Enfoque cuantitativo aplicado.
- Diseno experimental de laboratorio.
- Misma telemetria para ambos detectores.
- Repeticiones y etiquetas por escenario.

Idea visual:

- Diagrama: objetivos -> etapas -> evidencias.

Guion oral:

> La metodologia es cuantitativa y aplicada. Se construye un laboratorio donde los escenarios generan registros auditd, esos registros se procesan y alimentan dos detectores. La comparacion se realiza con las mismas etiquetas, las mismas ventanas de tiempo y las mismas metricas.

## 6. Arquitectura del laboratorio

Contenido maximo:

- VM Linux.
- auditd.
- Escenarios.
- Parser y variables.
- Reglas vs Isolation Forest.
- Comparacion.

Idea visual:

- Diagrama de arquitectura.

Guion oral:

> La arquitectura parte de una VM Linux instrumentada con auditd. Los escenarios generan eventos de ejecucion, cambios de permisos y actividad en un directorio de laboratorio. Luego un pipeline en Python transforma logs en variables y ejecuta dos rutas: reglas tipo SIEM e Isolation Forest.

## 7. Avance tecnico con capturas

Contenido maximo:

- VM creada.
- auditd activo.
- reglas auditctl.
- escenarios seguros.
- primeras consultas `ausearch`.

Idea visual:

- Collage de 3 a 4 screenshots.

Guion oral:

> En esta etapa el avance esperado es demostrar que el laboratorio existe y captura evidencia. No se presentan todavia resultados finales si no se han completado las repeticiones. Lo defendible aqui es la trazabilidad: escenario ejecutado, evento registrado, log procesado y variable construida.

## 8. Metricas de evaluacion

Contenido maximo:

- Detection rate / recall.
- False positive rate.
- Precision.
- F1 score.
- Tiempo de deteccion.

Idea visual:

- Matriz de confusion simple + tabla de formulas.

Guion oral:

> Las metricas permiten evaluar efectividad y costo operativo. La sensibilidad indica que tanto se detecta de lo sospechoso; la tasa de falsos positivos mide el ruido; la precision muestra que tan confiable es una alerta; el F1 resume precision y sensibilidad; y el tiempo de deteccion conecta el experimento con la operacion real de un SOC.

## 9. Resultados esperados y aporte

Contenido maximo:

- No declarar ganador aun.
- Comparar condiciones de mejor desempeno.
- Aporte: reducir ruido, decidir reglas vs ML, monitoreo Linux reproducible.

Idea visual:

- Tabla con columnas: reglas, ML, evidencia esperada.

Guion oral:

> El resultado esperado no es decir que Machine Learning siempre gana. El aporte es identificar bajo que condiciones las reglas son suficientes y bajo que condiciones un detector de anomalías aporta valor. Esto puede apoyar decisiones de monitoreo en Linux y reducir ruido operativo.

## 10. Cierre y proximos pasos

Contenido maximo:

- Ejecutar repeticiones.
- Consolidar dataset.
- Calcular metricas.
- Ajustar reglas/modelo.
- Preparar sustentacion final.

Idea visual:

- Roadmap corto.

Guion oral:

> Como proximos pasos estan completar las repeticiones, cerrar el dataset, calcular metricas comparables, ajustar umbrales y consolidar la discusion. La defensa de la primera sustentacion se centra en que el problema esta bien delimitado, la metodologia es coherente y el prototipo ya tiene una ruta tecnica reproducible.
