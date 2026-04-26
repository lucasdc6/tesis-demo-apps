## 5. Instrumentación

Tres aplicaciones desarrolladas en lenguajes y frameworks diferentes

<br>

| Aplicación | Lenguaje | Framework | Año | Instrumentación |
|---|---|---|---|---|
| **WordPress** | PHP | — | 2003 | Automática |
| **Redmine** | Ruby | Rails | 2006 | Manual |
| **Wagtail** | Python | Django | 2014 | Automática |

<br>

> _Ninguna fue diseñada teniendo en cuenta los 12 factores ni la observabilidad_

<!--v-->

## WordPress — PHP

Instrumentación automática sin tocar el código fuente de WordPress

**Dependencias:**

1. Extensiónes nativa PHP: `opentelemetry` · `protobuf`
2. Paquetes Composer: `opentelemetry-auto-wordpress` + SDK + exporter OTLP

**Activación transparente:**

```ini
; otel.php.ini
auto_prepend_file = ${OTEL_AUTOLOAD_PATH}
```

El intérprete ejecuta el autoload antes de cualquier script de WordPress,
inicializando el SDK de forma completamente transparente.

<!--v-->

## Wagtail — Python

Instrumentación con **cero modificaciones** al código fuente

```bash
# Durante la construcción de la imagen
opentelemetry-bootstrap -a install

# Entrypoint del contenedor
CMD ["opentelemetry-instrument", "uwsgi", "/app/etc/uwsgi.ini"]
```

El wrapper `opentelemetry-instrument` intercepta el proceso antes de que
la aplicación comience a procesar peticiones.

<!--v-->

## Redmine — Ruby

Instrumentación **manual** por falta de auto-instrumentador oficial en Ruby

**Inicializador** `config/initializers/otel.rb`:

```ruby
if ENV['OTEL_EXPORTER_OTLP_ENDPOINT'].present?
  require 'opentelemetry/sdk'
  require 'opentelemetry/exporter/otlp'
  require 'opentelemetry/instrumentation/all'

  OpenTelemetry::SDK.configure do |c|
    c.use_all()
    c.logger = Rails.logger
  end
end
```

La librería `opentelemetry-instrumentation-all` instrumenta ActiveRecord,
Action Pack, Net::HTTP y Redis mediante **monkey-patching**.

<!--v-->

### Redmine — Fluentd para logs

El SDK de Ruby **no soportaba exportar logs vía OTLP** al momento de implementar.

El formatter incluye `trace_id` y `span_id` en cada línea de log:

```ruby
if ENV['FLUENTD_URL']
  uri = URI.parse ENV['FLUENTD_URL']
  config.logger = Fluent::Logger::LevelFluentLogger.new(nil,
                                                        host: uri.host,
                                                        port: uri.port,
                                                        use_nonblock: true,
                                                        wait_writeable: false
                                                      )
  config.logger.formatter = proc do |severity, datetime, progname, message|
    map = { level: severity }
    map[:message]   = message if message
    map[:progname]  = progname if progname
    map[:service]   = uri.path[1..-1] if uri.path[1..-1]
    if ENV['OTEL_EXPORTER_OTLP_ENDPOINT'].present?
      map[:span_id]   = OpenTelemetry::Trace.current_span.context.hex_span_id
      map[:trace_id]  = OpenTelemetry::Trace.current_span.context.hex_trace_id
    end
    map
  end
  stdout_logger = ActiveSupport::Logger.new(STDOUT)
  config.logger.extend(ActiveSupport::Logger.broadcast(stdout_logger))
end

```

Esto preserva la **correlación entre logs y trazas** en Grafana.

<!--v-->

## Contenerización

Cada aplicación sigue el patrón de **imagen dual** (multi-stage build):

<div class="mermaid">
flowchart TD
    CF["Containerfile<br>multi-stage"]
    APP["stage: app<br>aplicación instrumentada"]
    NGX["stage: nginx<br>proxy reverso + archivos estáticos"]
    CF --> APP
    CF --> NGX
</div>

Toda la configuración se inyecta por **variables de entorno** (factor 3 de Twelve-Factor App):

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
OTEL_SERVICE_NAME=wordpress
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=production
```
