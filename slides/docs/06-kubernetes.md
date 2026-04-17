## 5. Despliegue en Kubernetes

Objetivo: demostrar el **escalado automático impulsado por telemetría**
en un entorno equivalente al productivo

<!--v-->

## Cluster local con _Kind_ (Kubernetes in Docker)

Infraestructura instalada con Helmfile:

| Componente | Rol |
|---|---|
| `NGINX Fabric` | Controlador de Gateway API, expone servicios en `*.localhost` |
| `KEDA` | Operador de escalado basado en métricas externas con soporte nativo para Prometheus |
| `Ganesha NFS` | Servidor NFS para volúmenes compartidos entre réplicas (ReadWriteMany) |
| `mysql-operator` | Operador para gestionar instancias de MySQL como recursos de Kubernetes |
| `CloudNativePG` | Operador para gestionar clústeres de PostgreSQL nativos en Kubernetes |

<!--v-->

## Cluster local con _Kind_ (Kubernetes in Docker)


| Componente | Rol |
|---|---|
| `Grafana` | Visualización unificada de las tres señales de observabilidad |
| `Mimir` | Almacenamiento de métricas compatible con la API de Prometheus |
| `Loki` | Almacenamiento de logs indexado por etiquetas |
| `Tempo` | Almacenamiento de trazas distribuidas multi-formato |
| `OpenTelemetry Collector` | Recolección, procesamiento y exportación centralizada de telemetría |

<!--v-->

## Helm Chart genérico

Un único chart en `helm/` despliega cualquiera de las tres aplicaciones.

Recursos generados por release:

- **Deployment** — pod con dos contenedores: app + sidecar Nginx
- **ConfigMap / Secret** — variables de entorno (credenciales, endpoints OTel)
- **Ingress** — expone el servicio en `<app>.localhost`
- **ScaledObject** — reglas de escalado horizontal con KEDA
- **PersistentVolumeClaim** — almacenamiento para archivos compartidos

<!--v-->

## Escalado automático con KEDA

**KEDA** (Kubernetes Event-Driven Autoscaling) escala Deployments
en respuesta a métricas externas al clúster.

```yaml
triggers:
  - type: prometheus
    metadata:
      serverAddress: http://lgtm-distributed-mimir-nginx.observability.svc/prometheus
      metricName: wagtail_request_rate
      threshold: "10"
      query: >
        sum(rate(
          traces_spanmetrics_calls_total{service_name="wagtail"}[1m]
        ))
```

Escala entre **1 y 5 réplicas** cuando supera **10 req/s por réplica**

<!--v-->

### La métrica `traces_spanmetrics_calls_total`

Generada automáticamente por el conector `spanmetrics` del OTel Collector
**a partir de las trazas**, sin instrumentación adicional.

<div class="mermaid">
flowchart TD
    A["Trazas de la app"] --> B["OTel Collector<br>spanmetrics connector"]
    B --> C["traces_spanmetrics_calls_total"]
    C --> D[("Mimir")]
    E["KEDA"] --> D
</div>

> _La misma telemetría que se consulta en Grafana alimenta la lógica de escalado_

<!--v-->

## Prueba de carga con Locust

Ingresar al sitio <a href="http://locust.localhost" target="_blank">Locust</a>


<!--v-->

### El ciclo observable en Grafana

1. **Tasa de peticiones en ascenso** → panel RED muestra el incremento en req/s
2. **KEDA evalúa el umbral** → consulta Mimir cada pocos segundos
3. **Scale-up** → nuevos pods pasan por `Pending → ContainerCreating → Running`
4. **Latencia se estabiliza** → el balanceador distribuye el tráfico entre réplicas
5. **Scale-down** → tras el `cooldownPeriod`, KEDA reduce a una réplica

<br>

> _Este ciclo cierra el argumento central: la observabilidad no solo describe
> el sistema, sino que puede **actuar sobre él** de forma autónoma_
