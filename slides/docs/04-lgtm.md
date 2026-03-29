## 3. Stack LGTM

Arquitectura de observabilidad open-source propuesta por **GrafanaLabs**

<br>

| Componente | Señal | Rol |
|---|---|---|
| **L**oki | Logs | Almacenamiento indexado por etiquetas |
| **G**rafana | — | Visualización y correlación unificada |
| **T**empo | Trazas | Almacenamiento eficiente multi-formato |
| **M**imir | Métricas | Almacenamiento compatible con API de Prometheus |

<br>

El **OTel Collector** actúa como intermediario central mediante OTLP

<!--v-->

## Grafana Mimir

Almacenamiento de métricas de **alta cardinalidad** y retención configurable

- Compatible con la API de Prometheus (PromQL)
- Acepta protocolo OTLP desde noviembre 2023
- Escala horizontalmente para grandes volúmenes

<br>

Usado en esta tesina como fuente de métricas para el escalado horizontal:

```promql
sum(rate(traces_spanmetrics_calls_total{service_name="<servicio>"}[1m]))
```

<!--v-->

## Grafana Loki

Almacenamiento de logs liviano: indexa **solo etiquetas**, no el contenido

<br>

Comparación con Elasticsearch (ELK):

| | Loki | Elasticsearch |
|---|---|---|
| Indexado | Solo labels | Contenido completo |
| Costo almacenamiento | Bajo | Alto |
| Integración Grafana | Nativa | Plugin |
| Consulta | LogQL | KQL / Lucene |

<!--v-->

## Grafana Tempo

Almacenamiento de trazas con integración nativa en Grafana

- Admite formatos: **OTLP · Jaeger · Zipkin**
- Navegación directa desde métricas y logs hacia trazas específicas
- Sampling configurable: head-based, tail-based, probabilístico

<!--v-->

## Arquitectura completa

<div class="mermaid">
flowchart LR
    WP["WordPress<br>PHP / OTLP HTTP :4318"]
    RM["Redmine<br>Ruby / OTLP HTTP :4318 & Fluentd :8006"]
    WG["Wagtail<br>Python / OTLP gRPC :4317"]
    OC["OTel Collector"]
    MM[("Mimir")]
    LK[("Loki")]
    TP[("Tempo")]
    GF["Grafana"]
    WP --> OC
    RM --> OC
    WG --> OC
    OC --> MM & LK & TP
    MM & LK & TP --> GF
</div>

<br>

El conector `spanmetrics` genera métricas RED a partir de trazas,
**sin instrumentación adicional**

Alternativamente, se puede utilizar la componente `Metrics-generator` de `Tempo`