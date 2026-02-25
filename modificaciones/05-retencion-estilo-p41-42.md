# Modificación 5 — Págs. 41–42: Inconsistencia de estilo en "Retención" (Grafana Mimir)

## Problema

En las páginas 41–42, la subsección **"Retención → Grafana Mimir"** utiliza un formato
tipográfico distinto al del resto del documento:

- Aparece un subtítulo en texto corrido en negrita con dos puntos:
  `**Implicaciones y Aspectos Clave de la Retención:**`
- Los ítems de la lista tienen **títulos en negrita** seguidos de una explicación:
  `● **Disponibilidad de Datos Históricos:** La retención define...`
  `● **Gestión del Almacenamiento:** La cantidad de datos...`

En todas las demás secciones del documento, las listas usan viñetas con texto plano
sin título en negrita (ver por ejemplo las listas de los 12 factores, pág. 52–53, o
los tipos de sampling, págs. 43–44). Este formato en negrita rompe la consistencia
visual y da la impresión de haber sido generado con una herramienta distinta.

## Texto original problemático (págs. 41–42)

```
**Implicaciones y Aspectos Clave de la Retención:**

● **Disponibilidad de Datos Históricos:** La retención define la ventana temporal
  dentro de la cual se pueden realizar consultas...
● **Gestión del Almacenamiento:** La cantidad de datos de métricas generados puede
  ser significativa...
● **Rendimiento de las Consultas:** Si bien Mimir está diseñado para manejar...
● **Cumplimiento Normativo y Auditoría:** En algunos casos, las regulaciones...
● **Optimización de Costos:** El almacenamiento de grandes cantidades...
● **Ciclo de Vida de los Datos:** La retención es una parte integral...
```

## Texto sugerido (con estilo consistente)

Convertir la lista con títulos en negrita a prosa corrida, manteniendo toda la
información pero con el mismo tono que el resto del documento:

---

> La retención de métricas en Grafana Mimir define el período durante el cual los datos
> están disponibles para su consulta, e impacta directamente en varias dimensiones
> operativas. En primer lugar, determina la **ventana de análisis histórico**: un período
> más largo permite identificar tendencias, comparar semanas o meses y diagnosticar
> problemas que ocurrieron en el pasado, aunque implica un mayor consumo de espacio de
> almacenamiento. En segundo lugar, incide en el **rendimiento de las consultas**, ya que
> Mimir organiza los datos en bloques y un rango temporal muy amplio puede incrementar
> el tiempo de ejecución de las mismas.
>
> Desde el punto de vista económico, la retención debe equilibrar la necesidad de
> datos históricos con el costo de almacenamiento, especialmente en entornos de nube
> donde dicho costo es directamente proporcional al volumen almacenado. En contextos
> regulados, la política de retención debe además alinearse con los requisitos de
> cumplimiento normativo y auditoría establecidos por la organización.
>
> Finalmente, la retención define cuándo los datos dejan de ser relevantes y pueden
> descartarse, constituyendo así una parte integral del ciclo de vida de las métricas.

---

## Nota

El mismo patrón de listas con títulos en negrita se repite en la subsección
**"Retención → Grafana Loki"** (págs. 42–43), aunque con menor extensión. Se
recomienda revisar también esa subsección para aplicar el mismo criterio de estilo.
