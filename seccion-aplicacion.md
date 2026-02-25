# Aplicación

Para las pruebas se seleccionaron tres productos desarrollados en lenguajes y frameworks
diferentes, con el fin de poder identificar y comparar las distintas formas de configurar la
instrumentación con OpenTelemetry en aplicaciones que no fueron diseñadas originalmente
con observabilidad en mente. Los casos de estudio seleccionados fueron:

- **WordPress**: un CMS desarrollado en PHP, publicado en el año 2003.
- **Redmine**: una herramienta de gestión de proyectos y tickets desarrollada en Ruby,
  usando el framework Ruby on Rails, publicada en el año 2006.
- **Wagtail**: un CMS desarrollado en Python, usando el framework Django, publicado
  en el año 2014.

Es importante destacar que ninguno de estos productos fue diseñado teniendo en cuenta los
12 factores descritos anteriormente, ni aplicando técnicas orientadas a facilitar la
observabilidad de sus componentes. Esto los convierte en casos de estudio representativos
del software preexistente que típicamente se encuentra en entornos productivos.

---

## Instrumentación

Para garantizar una instrumentación organizada y reproducible, se tomó como criterio base
que cada aplicación debía estar contenerizada y configurada para adherirse a los 12 factores.
Esto implicó revisar y ajustar los siguientes aspectos en cada una:

- **Configuración por variables de entorno**: toda configuración sensible al entorno
  (credenciales, endpoints, feature flags) se externaliza mediante variables de entorno,
  evitando valores fijos en el código o en archivos de configuración versionados.
- **Servicios de soporte declarados explícitamente**: bases de datos, cachés y gestores
  de sesiones se definen como servicios externos, lo que permite intercambiarlos o
  escalarlos de forma independiente.
- **Logs dirigidos a la salida estándar**: cada servicio envía sus registros a `stdout`,
  dejando al entorno de ejecución la responsabilidad de recolectarlos y enrutarlos.
  La excepción es Redmine, cuya estrategia de logging se detalla en la sección
  [Fluentd](#fluentd).
- **Paridad entre entornos**: la contenerización garantiza que el código base y sus
  dependencias sean idénticos entre el entorno de desarrollo y el productivo, eliminando
  discrepancias introducidas por diferencias en el sistema operativo o en las versiones
  de las dependencias.

---

## OpenTelemetry

Al instrumentar con OpenTelemetry, se pueden identificar dos enfoques según el grado de
intervención sobre el código fuente de la aplicación:

- **Instrumentación manual**: requiere instalar las dependencias del SDK de OpenTelemetry
  e incorporar llamadas explícitas en el código para crear y gestionar trazas y spans.
- **Instrumentación automática** (*zero-code instrumentation*): delega la lógica de
  instrumentación a bibliotecas especializadas que, mediante mecanismos propios del
  lenguaje (hooks, metaprogramación, monkey-patching, etc.), interceptan las operaciones
  relevantes sin necesidad de modificar el código de la aplicación.

### Instrumentación manual

#### Redmine

Redmine fue instrumentado de forma manual porque, al momento de realizar las pruebas,
no existía un proceso de instrumentación automática oficial de OpenTelemetry para Ruby.

La instrumentación de trazas se resuelve con la dependencia
`opentelemetry-instrumentation-all`, que provee instrumentaciones preempaquetadas para
los frameworks y bibliotecas más comunes del ecosistema Ruby on Rails (ActiveRecord,
Action Pack, Net::HTTP, Redis, entre otros). Esta biblioteca funciona mediante
metaprogramación: en lugar de modificar el código fuente de cada librería, extiende sus
clases en tiempo de carga aplicando *patches* que envuelven los métodos relevantes con
la lógica de apertura y cierre de spans.

A modo de ejemplo, la instrumentación de `ActiveRecord` se implementa extendiendo
`ActiveRecord::Base` con un módulo que redefine el método de consulta a la base de datos.
La clase de instrumentación registra el parche a través del método `install`:

```ruby
# instrumentation/active_record/lib/opentelemetry/instrumentation/active_record/instrumentation.rb
module OpenTelemetry
  module Instrumentation
    module ActiveRecord
      class Instrumentation < OpenTelemetry::Instrumentation::Base
        install do |_config|
          require_dependencies
          patch_activerecord
        end

        def patch_activerecord
          ::ActiveSupport.on_load(:active_record) do
            ::ActiveRecord::Base.prepend(Patches::Querying)
          end
        end
      end
    end
  end
end
```

El parche en sí utiliza el método de clase `prepended` para que, al ser extendida mediante
`prepend`, la clase incorpore los métodos definidos en el módulo `ClassMethods`. Dentro
de ese módulo, `define_method` selecciona el nombre de método correcto según la versión
de ActiveRecord, y lo redefine de modo que cada consulta quede envuelta en un span:

```ruby
# instrumentation/active_record/lib/opentelemetry/instrumentation/active_record/patches/querying.rb
module OpenTelemetry
  module Instrumentation
    module ActiveRecord
      module Patches
        module Querying
          def self.prepended(base)
            class << base
              prepend ClassMethods
            end
          end

          module ClassMethods
            method_name = ::ActiveRecord.version >= Gem::Version.new('7.0.0') \
              ? :_query_by_sql : :find_by_sql

            define_method(method_name) do |*args, **kwargs, &block|
              tracer.in_span("#{self} query") do
                super(*args, **kwargs, &block)
              end
            end
          end
        end
      end
    end
  end
end
```

Este patrón se repite para cada biblioteca instrumentada: `in_span` abre el span con un
nombre descriptivo, invoca la implementación original mediante `super`, y cierra el span
al terminar. Si se utilizara un ORM distinto a ActiveRecord que no esté incluido en las
instrumentaciones estándar de OpenTelemetry, sería necesario replicar esta lógica
manualmente para cada operación que se quiera rastrear.

Finalmente, para activar el SDK al iniciar la aplicación Rails se utiliza el mecanismo de
*initializers*: archivos Ruby que Rails ejecuta automáticamente durante el arranque.
El initializer agregado al proyecto, ubicado en `config/initializers/otel.rb`, tiene la
siguiente forma:

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

La inicialización está condicionada a la presencia de la variable de entorno estándar
`OTEL_EXPORTER_OTLP_ENDPOINT`. De esta forma, si la variable no está definida (por
ejemplo, en un entorno de desarrollo local sin colector), la aplicación arranca sin
instrumentación y sin errores. Cuando sí está presente, se cargan las dependencias, se
activan todas las instrumentaciones disponibles con `use_all()`, y se le pasa el logger
de Rails al SDK para que este pueda inyectar los identificadores de traza y span en cada
línea de log, habilitando la correlación entre ambas señales.

Como el SDK de OpenTelemetry para Ruby no incluye soporte para exportar logs directamente
mediante OTLP, el envío de registros se resolvió con una solución alternativa basada en
Fluentd, que se detalla en la sección siguiente.

---

### Instrumentación automática

La instrumentación automática fue utilizada tanto en WordPress como en Wagtail, ya que
ambos lenguajes (PHP y Python) cuentan con soporte oficial para este enfoque. Si bien la
lógica subyacente es equivalente, el mecanismo concreto para habilitarla difiere en cada
lenguaje.

#### WordPress

La instrumentación de WordPress requiere dos tipos de dependencias que se instalan por
separado:

1. **Extensiones nativas de PHP** (`opentelemetry` y `protobuf`), instaladas vía `pecl`
   durante la construcción de la imagen de contenedor.
2. **Dependencias de Composer** con la lógica de instrumentación específica para
   WordPress:

```json
{
  "name": "opentelemetry/wordpress-demo",
  "type": "project",
  "minimum-stability": "beta",
  "require": {
    "open-telemetry/opentelemetry-auto-wordpress": "^0.0.15",
    "open-telemetry/sdk": "^1.0",
    "open-telemetry/exporter-otlp": "^1.0",
    "php-http/guzzle7-adapter": "^1.0"
  },
  "config": {
    "allow-plugins": {
      "php-http/discovery": true
    }
  }
}
```

Dado que el objetivo de la instrumentación automática es no modificar el código fuente de
la aplicación, la activación del autoload de OpenTelemetry se realiza a través de la
directiva de PHP `auto_prepend_file`. Esta directiva instruye al intérprete para que
ejecute un archivo determinado antes de cualquier script de la aplicación, lo que permite
inicializar el SDK de OpenTelemetry de forma completamente transparente:

```ini
; otel.php.ini
auto_prepend_file = ${OTEL_AUTOLOAD_PATH}
```

La variable `OTEL_AUTOLOAD_PATH` se define en el `Containerfile` apuntando al archivo
`autoload.php` generado por Composer, que registra todas las dependencias de
instrumentación. De esta manera, OpenTelemetry queda inicializado antes de que WordPress
procese cualquier petición, sin necesidad de modificar ningún archivo del proyecto.

#### Wagtail

Para instrumentar un proyecto Python, es necesario instalar las dependencias de
OpenTelemetry. El paquete `opentelemetry-distro` incluye todas las instrumentaciones
automáticas disponibles para el ecosistema Python, mientras que
`opentelemetry-exporter-otlp` provee el exportador para enviar los datos al colector
mediante el protocolo OTLP:

```
# requirements.txt
-r requirements/production.txt
opentelemetry-distro==0.47b0
opentelemetry-exporter-otlp==1.26.0
```

Durante la construcción de la imagen, se ejecuta `opentelemetry-bootstrap -a install`,
que detecta automáticamente las bibliotecas instaladas en el entorno e instala las
instrumentaciones de OpenTelemetry correspondientes a cada una.

En tiempo de ejecución, la activación de la instrumentación se logra encapsulando el
servidor de aplicaciones (uWSGI) dentro del ejecutable `opentelemetry-instrument`, que
intercepta el proceso e inicializa el SDK antes de que la aplicación comience a procesar
peticiones:

```dockerfile
# Containerfile.wagtail
CMD ["opentelemetry-instrument", "uwsgi", "/app/etc/uwsgi.ini"]
```

Este enfoque no requiere ninguna modificación en el código fuente de Wagtail ni en su
configuración de Django, cumpliendo con el principio de instrumentación sin código.

---

## Fluentd

Esta solución fue implementada exclusivamente en Redmine para resolver una limitación
concreta: al momento de realizar las pruebas, el SDK de OpenTelemetry para Ruby no
contaba con soporte para exportar logs directamente mediante OTLP. Para mantener la
premisa de que la solución de observabilidad esté contenida en la propia aplicación, se
optó por Fluentd como puente entre la aplicación y el colector.

La configuración se realizó en el archivo `config/additional_environment.rb`, que es el
mecanismo que provee Rails para extender su configuración sin modificar los archivos
centrales del framework. Dicho archivo configura el logger de la aplicación de la
siguiente manera:

```ruby
config.lograge.enabled = true
config.logger = ActiveSupport::Logger.new(STDOUT)

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

Este diseño permite dos comportamientos simultáneos:

- **Salida estándar** (`stdout`): los logs se emiten en un formato legible para personas,
  útil durante el desarrollo y el debugging. Esto se logra mediante `broadcast`, que
  duplica cada mensaje de log hacia un segundo logger de stdout.
- **Envío a Fluentd**: los logs se emiten en formato JSON estructurado directamente al
  receptor `fluentforward` del colector de OpenTelemetry (escuchando en el puerto 8006).
  El formatter personalizado construye un mapa que incluye, cuando ambas variables de
  entorno están presentes, los campos `trace_id` y `span_id` extraídos del contexto
  activo de OpenTelemetry.

La inclusión de `trace_id` y `span_id` en cada entrada de log es el aspecto central de
esta solución: permite correlacionar un registro de log con la traza distribuida y el
span exacto que lo generaron. En la práctica, esto habilita flujos de análisis como
navegar desde una traza lenta en Tempo directamente hacia los logs asociados en Loki, o
identificar el span responsable de un error a partir de un mensaje de log.

---

## Contenerización

Las aplicaciones fueron contenerizadas fijando las versiones de los productos de dos
formas distintas según las posibilidades de cada ecosistema:

- **Redmine y WordPress**: se utiliza la imagen oficial de Docker, seleccionando la
  versión específica mediante el tag de la imagen (por ejemplo,
  `wordpress:6.5.4-php8.3-fpm` o `redmine:5.1.3-alpine`).
- **Wagtail**: se instala como dependencia de Python mediante `pip`, clonando la versión
  correspondiente del repositorio oficial durante la construcción de la imagen.

Cada aplicación sigue el patrón de imagen dual: un `Containerfile` multi-stage que
produce dos imágenes independientes a partir del mismo archivo, una para la aplicación
y otra para el servidor web Nginx que actúa como proxy reverso. Los archivos estáticos
(HTML, JS, CSS, imágenes, etc.) son servidos directamente por Nginx, mientras que el
tráfico dinámico es enrutado hacia la aplicación mediante `proxy_pass` (Redmine y
Wagtail) o `fastcgi_pass` (WordPress, dado que corre bajo PHP-FPM).

Todas las configuraciones —credenciales de bases de datos, endpoints del colector,
URLs de servicios externos— se gestionan exclusivamente mediante variables de entorno,
sin valores fijos en el código. Los archivos de configuración necesarios para cada
servicio son versionados junto al `Containerfile` y copiados al contenedor durante
la construcción, garantizando que cada imagen sea reproducible y autocontenida.

El entorno de desarrollo local se levanta con Docker Compose, utilizando un archivo base
que define la infraestructura de observabilidad (colector de OpenTelemetry, Mimir, Loki,
Tempo y Grafana) y archivos adicionales para cada aplicación demo. Esto permite iniciar
únicamente los servicios necesarios para cada caso de prueba y garantiza que el entorno
local sea funcionalmente equivalente al productivo.
