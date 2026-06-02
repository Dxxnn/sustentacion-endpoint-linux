---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-family: Arial, Helvetica, sans-serif;
    color: #17352a;
    background: #ffffff;
  }
  h1, h2 {
    color: #063b22;
    letter-spacing: 0;
  }
  h1 { font-size: 40px; }
  h2 { font-size: 34px; }
  strong { color: #0b7a3e; }
  .accent { color: #f58220; font-weight: 700; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: center; }
  .three { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; }
  .box { border-left: 8px solid #0b7a3e; padding: 14px 18px; background: #edf7f1; }
  .warn { border-left: 8px solid #f58220; padding: 14px 18px; background: #fff4e8; }
  table { font-size: 22px; }
  footer { color: #5b6b63; }
---

# Comparacion entre reglas tipo SIEM e Isolation Forest

## Cadenas de procesos sospechosas en endpoints Linux instrumentados con auditd

Daniel Esteban Lopez Suarez  
Ingenieria de Sistemas - Universidad EAN  
Primera sustentacion

<!--
Oral: Presenta el proyecto como una comparacion experimental, no como una promesa de que ML siempre gana.
-->

---

# Contexto: el ruido operativo en un SOC

<div class="grid">
<div>

- Analistas **L1, L2 y L3**
- Alertas desde **SIEM / EDR / telemetria**
- Muchos eventos son **falsos positivos**
- El problema: distinguir **secuencia legitima** vs **secuencia sospechosa**

</div>
<div class="warn">

**Idea clave**  
No falta telemetria: falta contexto para decidir si una cadena de procesos merece respuesta.

</div>
</div>

<!--
Oral: Arranca con el caso realista del SOC. Cada falso positivo consume tiempo y puede activar una respuesta innecesaria.
-->

---

# Pregunta y objetivos

**Pregunta:** ¿que diferencias de desempeño existen entre reglas tipo SIEM y un detector de anomalías con ML para identificar relaciones padre-hijo inusuales y descarga seguida de ejecucion?

<div class="three">
<div class="box"><strong>Laboratorio</strong><br/>VM Linux + auditd</div>
<div class="box"><strong>Escenarios</strong><br/>normal y sospechoso</div>
<div class="box"><strong>Evaluacion</strong><br/>deteccion, falsos positivos y tiempo</div>
</div>

<!--
Oral: Enfatiza que el objetivo general es comparar ambos enfoques bajo las mismas condiciones y con metricas homogeneas.
-->

---

# Estado del arte sintetizado

| Enfoque | Aporte | Limitacion |
|---|---|---|
| Reglas / SIEM | Explicabilidad y control | Rigidez ante variaciones |
| Anomalías / ML | Detecta desviaciones | Riesgo de falsos positivos |
| Logs modernos | Secuencias y grafos | Dependen de buena representacion |

**Brecha:** comparacion directa sobre procesos Linux con auditd en laboratorio local.

<!--
Oral: Menciona que la literatura reciente resalta la importancia de representar bien los registros, no solo elegir un modelo potente.
-->

---

# Metodologia experimental

![Flujo metodologia](assets/methodology_flow.svg)

<!--
Oral: Recorre las cinco etapas y conecta cada una con evidencia: VM, escenarios, logs, variables y comparacion.
-->

---

# Arquitectura del laboratorio

![Arquitectura laboratorio](assets/lab_architecture.svg)

<!--
Oral: Explica que auditd no es el detector; es la fuente de telemetria. La deteccion ocurre despues, con reglas y con Isolation Forest.
-->

---

# Avance tecnico: evidencia a mostrar

<div class="three">
<div class="box"><strong>1</strong><br/>VM Linux creada</div>
<div class="box"><strong>2</strong><br/>auditd activo</div>
<div class="box"><strong>3</strong><br/>reglas auditctl</div>
</div>

<div class="three">
<div class="box"><strong>4</strong><br/>escenarios seguros</div>
<div class="box"><strong>5</strong><br/>logs ausearch</div>
<div class="box"><strong>6</strong><br/>dataset inicial</div>
</div>

**Nota:** las metricas finales quedan pendientes hasta completar repeticiones.

<!--
Oral: No vendas resultados. Vende trazabilidad: escenario ejecutado, log capturado, variable construida.
-->

---

# Metricas de evaluacion

| Metrica | Que responde |
|---|---|
| Recall / tasa de deteccion | ¿cuanto de lo sospechoso detecta? |
| Tasa de falsos positivos | ¿cuanto ruido produce? |
| Precision | ¿que tan confiable es la alerta? |
| F1 score | ¿como equilibra precision y recall? |
| Tiempo de deteccion | ¿que tan rapido alerta? |

<!--
Oral: Relaciona las metricas con la operacion del SOC: detectar mas no sirve si el ruido vuelve inmanejable la respuesta.
-->

---

# Resultados esperados y aporte

<div class="grid">
<div>

**Reglas tipo SIEM**

- Interpretables
- Buenas para patrones definidos
- Requieren mantenimiento

</div>
<div>

**Isolation Forest**

- Aprende linea base
- Puede detectar desviaciones
- Requiere calibrar falsos positivos

</div>
</div>

<div class="warn">Aporte: reducir ruido operativo y apoyar decisiones de monitoreo en Linux con evidencia reproducible.</div>

<!--
Oral: La contribucion es comparativa y practica. No declares ganador antes de medir.
-->

---

# Cierre y proximos pasos

1. Completar repeticiones por escenario.
2. Consolidar dataset auditd.
3. Calcular matriz de confusion y tiempos.
4. Ajustar reglas y umbral del modelo.
5. Preparar sustentacion final con resultados validados.

**Mensaje final:** problema delimitado, metodologia coherente y prototipo reproducible.

<!--
Oral: Cierra con seguridad: la primera sustentacion prueba claridad, avance y ruta tecnica defendible.
-->
