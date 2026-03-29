## 1. Conceptos básicos

> _"Propiedad que le permite a las personas y máquinas observar, entender
> y actuar en respuesta al estado interno de un sistema"_

Los sistemas exponen su estado a través de **señales**, clasificadas en tres pilares:

- **Métricas** — valores numéricos agregables a lo largo del tiempo
- **Logs** — eventos discretos con contexto textual
- **Trazas** — flujo de un requerimiento a través de múltiples servicios

<!--v-->

### Los tres pilares

<br>

| Pilar | Volumen | Característica |
|---|---|---|
| Métricas | Menor | Agrupables, ideales para alertas y escalado |
| Logs | Mayor | Eventos no distribuidos, detalle de operaciones |
| Trazas | Mayor | Eventos distribuidos, visibilidad end-to-end |

<br>

> _Fuente: CNCF TAG Observability Whitepaper_

<!--v-->

## Métricas

Valores numéricos que representan el estado de un recurso en un instante de tiempo.

Compuestas por: **nombre** · **timestamp** · **valor** · **labels**

<br>

Conjuntos de métricas estándar:

| Método | Siglas | Aplica a |
|---|---|---|
| **USE** | Utilización · Saturación · Errores | Recursos (CPU, memoria, red) |
| **RED** | Rate · Errors · Duration | Servicios web |
| **Golden Signals** | Latencia · Tráfico · Errores · Saturación | Sistemas distribuidos (Google SRE) |

<!--v-->

### Modelos de recolección

<br>

- **Push** — el servicio envía los datos al backend

    - Lógica distribuida en cada agente
    - Complejidad crece con el número de servicios
    - Ejemplo: stack TICK (Telegraf · InfluxDB · Chronograf · Kapacitor)

- **Pull** — el backend recupera los datos de los exporters

    - Configuración centralizada
    - Ejemplo: Prometheus + node-exporter

<!--v-->

## Logs

Describen **eventos discretos** que ocurren en un instante de tiempo.

Características clave:

- Representados por timestamp + mensaje (texto plano o estructurado)
- Deben escribirse a **stdout/stderr** (factor 11 de Twelve-Factor App)
- Formato estructurado (JSON, Logfmt) facilita el procesamiento centralizado

<br>

Formatos comunes: **CLF** (Nginx/Apache) · **Logfmt** · **Syslog** (RFC 3164 / RFC 5424)

<!--v-->

## Trazas

Describen el **flujo completo de un requerimiento** desde que ingresa al sistema hasta que retorna al usuario.

Unidad mínima: el **Span** — representa una operación con duración medible

<div class="mermaid">
gantt
    dateFormat x
    axisFormat %Lms
    section GET /api/posts [52ms]
    GET /api/posts        :0, 52
    wpdb.query SELECT     :5, 14
    wpdb.query SELECT     :16, 17
    wpdb.connect          :20, 29
</div>

<!--v-->

### Correlación de señales

Las tres señales pueden relacionarse entre sí mediante metadatos compartidos:

| Mecanismo | Descripción |
|---|---|
| **Ventana temporal** | Filtrar las tres señales por el mismo instante |
| **Request / Trace ID** | Navegar de logs a la traza exacta del requerimiento |
| **Exemplars** | Enlace directo desde una métrica a la traza que la generó |

<br>

> _La correlación transforma datos aislados en información accionable_
