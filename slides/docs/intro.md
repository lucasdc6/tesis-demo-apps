# Observabilidad

## una base para aplicaciones resilientes

<br>

**Lucas Di Cunzolo**

Director: Miguel Angel Luengo · Codirector: Christian Adrian Rodriguez

Asesor profesional: Leandro Di Tommaso

<br>

_Licenciatura en Informática — UNLP, Facultad de Informática_

_Marzo 2026_

<!--s-->

## Contexto

El desarrollo de aplicaciones web ha experimentado cambios disruptivos en los últimos años:

- Las **metodologías ágiles** aceleraron los ciclos de entrega
- Surgió **DevOps** como respuesta a la necesidad de alinear desarrollo y operaciones
- La infraestructura evolucionó hacia modelos **cloud-native** y contenedores
- Kubernetes estandarizó la gestión de infraestructuras complejas

<!--v-->

### La complejidad crece

Con arquitecturas distribuidas y microservicios:

- Múltiples servicios heterogéneos conviven en el mismo ecosistema
- Cada componente puede escalar de forma independiente
- Los contenedores son **efímeros**: visualizar logs ya no es trivial
- Un incidente puede originarse en cualquier punto de la cadena

> _Cuando algo falla en producción, ¿sabemos dónde mirar?_

<!--v-->

## Problema

Los sistemas modernos exigen **99,9% de disponibilidad**

Los servicios se degradan ante picos de demanda imprevistos

Sin visibilidad interna, diagnosticar un incidente puede llevar horas

<br>

### ¿Cómo comprender el comportamiento de un sistema en su ambiente productivo, independientemente de la tecnología?

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

<!--v-->

## Estructura de la presentación

1. **Conceptos básicos** — métricas, logs y trazas
2. **OpenTelemetry** — el estándar unificador
3. **Stack LGTM** — Loki, Grafana, Tempo, Mimir
4. **Instrumentación** — WordPress, Redmine y Wagtail
5. **Despliegue en Kubernetes** — Helm, KEDA y escalado automático
6. **Conclusiones**
