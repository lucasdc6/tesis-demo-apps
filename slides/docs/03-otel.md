## 3. OpenTelemetry

**El estándar unificador de telemetría en entornos cloud-native**

<br>

Proyecto de la **CNCF** (Cloud Native Computing Foundation), fusión de OpenTracing y OpenCensus en 2019.

Unifica las tres señales bajo un único protocolo: **OTLP** _(OpenTelemetry Protocol)_

> _Antes de OTel: un vendor diferente por cada señal, vendor lock-in en cada capa_

Notes:
- Sin OTel, uno está a la merced de que datos expone
- Multiplicidad de vendor para conseguir la imagen completa

<!--v-->

## Componentes de OpenTelemetry

<br>

| Componente | Rol |
|---|---|
| **API** | Interfaz para instrumentar código, agnóstica al backend |
| **SDK** | Implementación de la API con pipelines de exportación |
| **Auto-instrumentación** | Intercepta frameworks sin modificar el código fuente |
| **OTel Collector** | Agente intermediario: recibe, procesa y exporta señales |
| **OTLP** | Protocolo de transporte unificado (gRPC / HTTP) |

<!--v-->

### OTel Collector

Desacopla la generación de telemetría del almacenamiento:

<div class="mermaid">
flowchart LR
    A[Aplicaciones] -->|OTLP| R[Receiver]
    subgraph Outer[<br>Collector]
        R --> P[Processor<br>batch · atributos · filtros]
        P --> E[Exporter]
    end
    E --> M[(Mimir<br>métricas)]
    E --> L[(Loki<br>logs)]
    E --> T[(Tempo<br>trazas)]
</div>

<br>

Ventajas:
- Cambiar el backend **sin tocar las aplicaciones**
- El collector puede escalar horizontalmente
- Buffer local ante indisponibilidad de las bases de datos
- Conector `spanmetrics` ➜ deriva métricas RED directamente desde trazas

<!--v-->

## Instrumentación automática vs manual

<br>

**Automática** _(zero-code instrumentation)_

- Intercepta frameworks mediante hooks, monkey-patching o metaprogramación
- No requiere modificar el código fuente
- Soporte varía según el lenguaje y framework

<br>

**Manual**

- Instala el SDK e incorpora llamadas explícitas para crear spans
- Mayor control y granularidad
- Necesaria cuando no hay auto-instrumentador disponible

<br>

> _En esta tesina: automática en PHP y Python · manual en Ruby_

Notes:
- Los casos de Java y .NET son similares, siendo los más maduros