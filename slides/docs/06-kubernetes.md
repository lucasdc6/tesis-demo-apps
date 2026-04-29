## 6. Despliegue en Kubernetes

Objetivo: demostrar el **escalado automático impulsado por telemetría**
en un entorno equivalente al productivo

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

Escala entre **1 y 10 réplicas** cuando supera **10 req/s por réplica**

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

Ingresar al sitio <a href="https://locust.tesis.lucasdc.ar" target="_blank">Locust</a>

Luego, visualizar los datos en <a href="https://grafana.tesis.lucasdc.ar" target="_blank">Grafana</a>


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
