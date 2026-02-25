# Modificación 3 — Pág. 72: Sección "Fluentd" con frase cortada

## Problema

En la página 72, la subsección **"Fluentd"** contiene la frase:

> "Para instrumentar fluentd"

…seguida de un salto de párrafo y luego el texto "A su vez permite…" que continúa
como si lo anterior estuviera completo. La oración introductoria quedó sin terminar:
no tiene punto final ni contenido que describa el proceso de configuración de Fluentd.
Esta es la sección más relevante para explicar cómo se resolvió la correlación de
logs y trazas en Redmine, por lo que su ausencia es significativa.

## Texto sugerido

Reemplazar la frase incompleta "Para instrumentar fluentd" con el siguiente párrafo,
que reconstruye el contenido a partir de los archivos de configuración del repositorio
(`etc/ruby/additional_environment.rb`):

---

> Para instrumentar Fluentd, se configuró el servidor de Fluentd como receptor de logs
> en el mismo contenedor de Redmine, escuchando en el puerto local 24224 mediante el
> protocolo `forward`. En el lado de Rails, se utilizó la gema `fluent-logger` para
> enviar los eventos de log directamente a ese receptor. La configuración se realizó en
> el archivo `additional_environment.rb`, que Rails ejecuta al inicializar el objeto
> `config` de la aplicación. En dicho archivo se define un formateador personalizado que
> serializa cada evento de log como un objeto JSON que incluye, además del mensaje y el
> nivel de severidad, los campos `trace_id` y `span_id` extraídos del contexto activo de
> OpenTelemetry. De esta forma, cada registro de log queda vinculado a la traza
> correspondiente al requerimiento que lo originó.
>
> A su vez, para mantener legibilidad en la salida estándar del contenedor —que es
> consumida por los operadores en tiempo real—, se configuró un segundo logger que emite
> en formato texto plano hacia `STDOUT`. Grafana Loki recibe los logs estructurados
> provenientes de Fluentd y los almacena con los campos `trace_id` y `span_id` como
> etiquetas de correlación, habilitando la navegación directa desde Grafana Tempo hacia
> los logs asociados a una traza específica.

---

## Contexto técnico de apoyo

El archivo `etc/ruby/additional_environment.rb` del repositorio configura:

```ruby
config.logger = ActiveSupport::Logger.new(STDOUT)
fluent_logger = Fluent::Logger::FluentLogger.new(nil, host: 'localhost', port: 24224)
# Formatter que inyecta trace_id y span_id en el payload JSON enviado a Fluentd
```

## Ubicación exacta en el documento

Reemplazar el fragmento de la página 72 que dice:

```
Para instrumentar fluentd

A su vez permite, mediante el uso de distintos loggers...
```

Por el texto sugerido arriba, que fusiona ambos párrafos en una sección coherente.
