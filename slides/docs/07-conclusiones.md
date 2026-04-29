## 7. Conclusiones

<!--v-->

### Objetivo cumplido

Se instrumentaron tres aplicaciones en lenguajes distintos
**sin modificar su código fuente**, centralizando la telemetría
en un stack open-source unificado.

Las pruebas fueron desplegadas en 2 entornos:

- **Docker Compose** — desarrollo local e inspección de trazas
- **Kubernetes (Kind)** — escalado automático impulsado por telemetría

<!--v-->

## Sobre las señales de la observabilidad

Las tres señales son **complementarias**, no redundantes:

| Señal | Valor |
|---|---|
| **Métricas** | Estado general del sistema · insumo para alertas y escalado |
| **Logs** | Detalle de eventos en la aplicación |
| **Trazas** | Flujo completo de un requerimiento entre todos los componentes |

<br>

El valor emergente aparece al **correlacionarlas**: navegar de una alerta
en métricas hasta la traza del requerimiento afectado y sus logs exactos
reduce significativamente el **MTTR** _(Mean Time To Resolution)_.

<!--v-->

## Sobre OpenTelemetry

Resuelve la fragmentación histórica de herramientas propietarias:

- Protocolo de transporte unificado **OTLP** para las tres señales
- SDKs para los principales lenguajes de programación
- Auto-instrumentación que elimina la necesidad de modificar el código
- El **OTel Collector** desacopla la recolección del almacenamiento

<br>

Su adopción por **GrafanaLabs, New Relic y Datadog** confirma que OTLP
se proyecta como la interfaz universal de la telemetría en la industria.

<!--v-->

## Sobre la observabilidad y la resiliencia

> _La adaptación automática solo es posible si el sistema
> tiene visibilidad sobre su propio estado._

<br>

En la PoC, KEDA escala cada Deployment en función de
`traces_spanmetrics_calls_total`, derivada de las trazas:

- Sin cambios adicionales en la instrumentación
- La misma telemetría que diagnostica un problema **lo resuelve**
- Demuestra que la observabilidad es una **base para la resiliencia**

<!--v-->

## Trabajos futuros

- **Rollbacks automatizados** impulsados por telemetría post-despliegue
- **Service mesh** (Istio / Linkerd) para trazas y métricas a nivel de red
- **Profiling** como cuarta señal (en desarrollo activo en OTel)
- Extensión a arquitecturas **multi-cluster** y entornos cloud

<!--v-->

## Gracias

<br>

**Lucas Di Cunzolo**

Director: Miguel Angel Luengo

Codirector: Christian Adrian Rodriguez

Asesor profesional: Leandro Di Tommaso

<br>

_Licenciatura en Informática — UNLP, Facultad de Informática_

_Abril 2026_