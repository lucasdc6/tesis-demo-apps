# Aplicaciones demo

Repositorio de la PoC de la tesis **"Observabilidad, una base para aplicaciones resilientes"**.

El objetivo es demostrar cómo instrumentar con OpenTelemetry tres aplicaciones preexistentes,
desarrolladas en lenguajes y frameworks distintos, sin modificar su código fuente, y centralizar
sus señales de telemetría (trazas, métricas y logs) en un stack de observabilidad unificado.

## Qué incluye

### Aplicaciones instrumentadas

| Aplicación | Lenguaje | Framework | Instrumentación |
|------------|----------|-----------|-----------------|
| WordPress  | PHP 8.3  | —         | Automática (extensión PECL + Composer) |
| Redmine    | Ruby     | Rails     | Manual (SDK + `opentelemetry-instrumentation-all`) |
| Wagtail    | Python 3.9 | Django  | Automática (`opentelemetry-instrument`) |

### Stack de observabilidad

- **OpenTelemetry Collector** — recibe las señales de todas las aplicaciones (OTLP HTTP/gRPC y Fluentd) y las enruta a los backends.
- **Mimir** — almacenamiento de métricas (compatible con Prometheus).
- **Loki** — almacenamiento de logs.
- **Tempo** — almacenamiento de trazas distribuidas.
- **Grafana** — visualización unificada de las tres señales.

### Estructura del repositorio

```
├── bin/                    # Scripts para gestionar el ambiente (service-run, service-stop, etc.)
├── compose_files/          # Archivos Docker Compose por servicio
├── container_files/        # Containerfiles multi-stage para cada aplicación
├── etc/                    # Configuración de servicios
│   ├── grafana/            #   Datasources, Mimir, Loki, Tempo, Alertmanager
│   ├── mysql/              #   Script de inicialización de bases de datos
│   ├── nginx/              #   Templates de configuración del LB y proxies por app
│   ├── otel/               #   Pipeline del OpenTelemetry Collector
│   ├── php/                #   Extensión OTel, composer.json para WordPress
│   ├── python/             #   Dependencias y configuración para Wagtail
│   └── ruby/               #   Gemfile, initializer OTel y config de logs para Redmine
├── data/                   # Salida JSON del OTel Collector (generada en runtime)
├── helm/                   # Helm chart genérico para desplegar las apps en Kubernetes
└── kubernetes/             # Config de cluster Kind y releases con Helmfile
```

## Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

> Los scripts en `bin/` se agregan automáticamente al `PATH` si se usa [direnv](https://direnv.net/) con el `.envrc` incluido.

## Iniciar el ambiente

Los servicios se gestionan con los scripts del directorio `bin/`. El argumento puede ser
`base`, `wordpress`, `redmine`, `wagtail` o `all` (también se aceptan las abreviaciones
`b`, `wp`, `r`, `wt`).

**1. Iniciar la infraestructura base** (obligatorio, debe ejecutarse primero):

```bash
./bin/service-run base
```

Esto levanta el colector de OpenTelemetry, Grafana, Mimir, Loki, Tempo y el proxy Nginx.

**2. Levantar una o más aplicaciones demo:**

```bash
./bin/service-run wordpress
./bin/service-run redmine
./bin/service-run wagtail
```

O todas a la vez:

```bash
./bin/service-run all
```

## URLs de acceso

Una vez levantado el ambiente:

| Servicio   | URL                          | Credenciales   |
|------------|------------------------------|----------------|
| Grafana    | http://grafana.localhost     | N/A            |
| WordPress  | http://wordpress.localhost   | admin/admin    |
| Redmine    | http://redmine.localhost     | admin/admin    |
| Wagtail    | http://wagtail.localhost     | admin/changeme |

> Grafana está configurado con acceso anónimo en rol de administrador. No requiere login.

## Destruir el ambiente

```bash
./bin/service-stop all
```

> **Atención**: este comando ejecuta `docker compose down -v`, por lo que elimina los contenedores
> **y todos los volúmenes** asociados (bases de datos, datos de Mimir/Loki/Tempo, etc.).
> Los datos generados no son recuperables luego de ejecutarlo.

Para detener únicamente una aplicación específica sin afectar el resto:

```bash
./bin/service-stop wordpress
```

## Otros comandos

```bash
# Reconstruir las imágenes de contenedor
./bin/service-build <DEMO>

# Ver logs en tiempo real
./bin/service-logs <DEMO>
```

## Estresar las aplicaciones con Locust

El directorio `locust/` contiene archivos de prueba de carga para cada aplicación:

| Archivo             | Aplicación                              |
|---------------------|-----------------------------------------|
| `locust/wordpress.py` | WordPress                             |
| `locust/redmine.py`   | Redmine                               |
| `locust/wagtail.py`   | Wagtail                               |
| `locust/all.py`       | Las tres aplicaciones simultáneamente |

No hace falta instalar Locust: se puede correr directamente con Docker.

### Estresar una aplicación individual

```bash
docker run --rm \
  --network=host \
  -v $(pwd)/locust:/mnt/locust \
  locustio/locust \
  -f /mnt/locust/wordpress.py \
  --host=http://wordpress.localhost
```

Reemplazar `wordpress.py` y `wordpress.localhost` por la aplicación deseada.
Luego abrir http://localhost:8089 para configurar la cantidad de usuarios y arrancar la prueba.

### Estresar las tres aplicaciones a la vez

```bash
docker run --rm \
  --network=host \
  -v $(pwd)/locust:/mnt/locust \
  locustio/locust \
  -f /mnt/locust/all.py
```

`all.py` define un host por clase de usuario, por lo que no es necesario especificar `--host`.

### Modo headless (sin interfaz web)

```bash
docker run --rm \
  --network=host \
  -v $(pwd)/locust:/mnt/locust \
  locustio/locust \
  -f /mnt/locust/all.py \
  --headless \
  --users 20 \
  --spawn-rate 5 \
  --run-time 2m
```
