# Índice de modificaciones sugeridas

Revisión completa del documento `Tesis.pdf`. Se identificaron **6 problemas** que afectan
la calidad académica del texto: dos secciones sin contenido, dos secciones con texto
cortado, un error tipográfico de nombre propio y un problema de estilo/consistencia.

---

## Resumen

| # | Archivo | Página | Tipo | Gravedad |
|---|---------|--------|------|----------|
| 1 | `01-correlacion-tableros-p35.md` | 35 | Sección vacía | 🔴 Alta |
| 2 | `02-typo-jaeger-p46.md` | 46 | Error tipográfico | 🔴 Alta |
| 3 | `03-fluentd-incompleto-p72.md` | 72 | Texto cortado | 🔴 Alta |
| 4 | `04-contenerizacion-incompleta-p73.md` | 73 | Texto cortado | 🟠 Media |
| 5 | `05-retencion-estilo-p41-42.md` | 41–42 | Inconsistencia de estilo | 🟡 Baja |
| 6 | `06-ejemplo-http-500-p31.md` | 31 | Error conceptual menor | 🟡 Baja |

---

## Detalle de cada problema

### 1 — Pág. 35: Sección "Correlación entre tableros" vacía
El título existe en el documento (también aparece en el índice, pág. 2) pero no tiene
ningún párrafo de contenido. Es la única subsección de "Visualización y tratamiento de
la información" que queda sin desarrollar.

### 2 — Pág. 46: Error tipográfico "Jagger" → "Jaeger"
El nombre de la herramienta de trazas distribuidas desarrollada por Uber se escribe
**Jaeger**, no "Jagger". El error aparece dos veces en el mismo párrafo.

### 3 — Pág. 72: Sección "Fluentd" con frase cortada
La frase "Para instrumentar fluentd" termina sin punto ni contenido. El párrafo
siguiente ("A su vez permite…") continúa como si lo anterior estuviera completo, pero
claramente falta la descripción del proceso de configuración de Fluentd.

### 4 — Pág. 73: Sección "Contenerización" con frase incompleta
La sección cierra con "La configuración del ambiente de desarrollo local puede hacerse
usando docker" — oración sin verbo principal ni punto final, que corta abruptamente
antes del titular de "Conclusiones".

### 5 — Págs. 41–42: Estilo inconsistente en subsección "Retención" (Grafana Mimir)
El encabezado "**Implicaciones y Aspectos Clave de la Retención:**" y los ítems con
títulos en negrita rompen la consistencia visual del documento, que en el resto de las
secciones utiliza viñetas con texto plano.

### 6 — Pág. 31: Código de error HTTP 501 en el ejemplo de alerta
El ejemplo práctico de correlación de señales usa el código HTTP **501** (Not
Implemented) como base de una alerta por "demasiados errores". El código más
representativo para este tipo de alerta es el **500** (Internal Server Error) o la familia
**5xx** en general.
