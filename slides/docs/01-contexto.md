## 1. Contexto

El desarrollo de aplicaciones web ha experimentado cambios disruptivos en los últimos años:

- Las **metodologías ágiles** aceleraron los ciclos de entrega
- Surgió **DevOps** como respuesta a la necesidad de alinear desarrollo y operaciones
- La infraestructura evolucionó hacia modelos **cloud-native** y contenedores
- Surgieron varios productos (_vendors_) que ofrecían visibilidad usando diversos tipos de datos
- Kubernetes estandarizó la gestión de infraestructuras complejas

Notes:
- 2001: Manifiesto por el Desarrollo Ágil de Software
- 2009: DevOps

<!--v-->

### Evolución histórica

<br>

<div class="mermaid">
---
config:
  theme: 'forest'
  themeVariables:
    primaryColor: '#dfa1a1'
    secondaryColor: '#a5bee9'
    tertiaryColor: '#50c9a5'
    primaryTextColor: '#000000'
---
timeline
    2012 : SoundCloud ➜ Prometheus
         : Twitter ➜ Zipkin<br>─────────<br>Primer OSS de trazas
    2014 : Google ➜ Kubernetes<br>───────<br>Primer release pública
    2015 : Uber ➜ Jaeger<br>─────────<br>Escalabilidad + UI
         : CNCF ➜ Kubernetes <br>────────────<br>Primer proyecto incubado de la CNCF
    2016 : CNCF ➜ Prometheus<br>────────<br>Segundo proyecto incubado de la CNCF
    2018 : CNCF ➜ Prometheus<br>────────<br>Proyecto graduado de la CNCF
    2019 : OpenTracing + OpenCensus ➜ OpenTelemetry
         : Grafana ➜ Loki
    2020 : Prometheus ➜ OpenMetrics 1.0
         : Grafana ➜ Tempo
    2022 : Grafana ➜ Mimir
    2023 : Grafana adopta OTLP
</div>

Notes:
- CNCF fundadores: Google, CoreOS, Red Hat, Twitter, Huawei, Intel, Cisco, IBM, Docker, VMware
- En marzo salió el primer RC de OpenMetrics 2.0

<!--v-->

### La complejidad crece

Con arquitecturas distribuidas y microservicios:

- Múltiples servicios heterogéneos conviven en el mismo ecosistema
- Cada componente puede escalar de forma independiente
- Los contenedores son **efímeros**: visualizar logs ya no es trivial
- Un incidente puede originarse en cualquier punto de la cadena

> _Cuando algo falla en producción, ¿sabemos dónde mirar?_

<!--v-->

## Problemas

- Los sistemas modernos exigen **99,9% de disponibilidad**

- Los servicios se degradan ante picos de demanda imprevistos

- Sin visibilidad interna, diagnosticar un incidente puede llevar horas

<br>

#### ¿Cómo comprender el comportamiento de un sistema en su ambiente productivo, independientemente de la tecnología?

<!--v-->

## Objetivo

Identificar los mecanismos necesarios para **comprender y reconocer el desempeño**
de los sistemas en producción, de forma agnóstica a la tecnología.

<br>

Con el fin de poder:

- Anticipar potenciales problemas
- Determinar bajo qué condiciones escalar un servicio
- Reducir el tiempo de diagnóstico ante incidentes
- Automatizar la resiliencia mediante telemetría

<!--v-->

## Resiliencia

Una aplicación es **resiliente** si puede adaptarse ante eventos nuevos
sin degradar la calidad del servicio.

<br>

Estrategias estudiadas:

| Estrategia | Descripción |
|---|---|
| Arquitecturas distribuidas | Alta disponibilidad mediante múltiples zonas |
| Auto-sanado _(self-healing)_ | Health checks + reinicio automático ante fallos |
| **Escalado adaptativo** | Escalar horizontal o verticalmente según indicadores |

<br>

> _Esta tesina se enfoca en la **adaptabilidad de servicio** como estrategia de resiliencia._
