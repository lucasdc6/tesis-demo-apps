## 5. Despliegue en Kubernetes

Objetivo: demostrar el **escalado automático impulsado por telemetría**
en un entorno equivalente al productivo

<br>

Cluster local con **Kind** (Kubernetes in Docker)

Infraestructura instalada con Helmfile:

| Componente | Rol |
|---|---|
| `ingress-nginx` | Controlador de Ingress, expone servicios en `*.localhost` |
| `KEDA` | Operador de escalado basado en métricas externas |
| `lgtm-distributed` | Stack de observabilidad: Loki + Grafana + Tempo + Mimir |

<!--v-->

## Helm Chart genérico

Un único chart en `helm/` despliega cualquiera de las tres aplicaciones.

Recursos generados por release:

- **Deployment** — pod con dos contenedores: app + sidecar Nginx
- **ConfigMap / Secret** — variables de entorno (credenciales, endpoints OTel)
- **Ingress** — expone el servicio en `<app>.localhost`
- **ScaledObject** — reglas de escalado horizontal con KEDA
- **PersistentVolumeClaim** — almacenamiento para archivos de usuario (WordPress, Wagtail)

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
    D --> E["KEDA"]
</div>

> _La misma telemetría que se consulta en Grafana alimenta la lógica de escalado_

<!--v-->

## Prueba de carga con Locust

Scripts de Locust simulan usuarios navegando las tres aplicaciones:

```bash
locust -f locust/all.py \
  --users 50 --spawn-rate 5 \
  --headless --run-time 3m
```

Pesos: WordPress 3x · Redmine 2x · Wagtail 2x

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
