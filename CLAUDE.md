# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a thesis demo environment for **"Observabilidad, una base para aplicaciones resilientes"** (Observability, a foundation for resilient applications). It showcases OpenTelemetry instrumentation across three web frameworks (PHP/WordPress, Ruby/Redmine, Python/Wagtail) with a full observability stack.

## Service Management Commands

The `bin/` directory is added to `PATH` via `.envrc` (direnv). All commands accept a `<DEMO>` argument: `base`, `wordpress`, `redmine`, `wagtail`, or `all`.

```bash
service-run <DEMO>    # Start services (docker compose up)
service-stop <DEMO>   # Stop and remove containers (-v also removes volumes)
service-build <DEMO>  # Build container images
service-logs <DEMO>   # View service logs
```

Example workflow:
```bash
service-run base        # Always start base infrastructure first
service-run wordpress   # Then start individual demos
service-run all         # Or start everything at once
service-stop all        # Cleanup
```

## Local Access URLs

- http://grafana.localhost — Grafana dashboards (anonymous admin)
- http://wordpress.localhost — WordPress CMS
- http://redmine.localhost — Redmine project manager
- http://wagtail.localhost — Wagtail CMS

## Architecture

### Docker Compose Structure

| File | Contents |
|------|----------|
| `compose_files/docker-compose.yaml` | Base infrastructure: MySQL, Nginx LB, OTel Collector, Grafana, Mimir, Loki, Tempo |
| `compose_files/docker-compose.wordpress.yaml` | WordPress (PHP-FPM) + Nginx sidecar |
| `compose_files/docker-compose.redmine.yaml` | Redmine (Rails) + Nginx sidecar + migration job |
| `compose_files/docker-compose.wagtail.yaml` | Wagtail (Django) + Postgres + Redis + Nginx sidecar |

Each application stack uses three isolated Docker networks: `app` (frontend), `backend` (databases), `observability` (monitoring).

### Observability Data Flow

```
WordPress (PHP/OTLP HTTP:4318)  ─┐
Redmine   (Ruby/Fluentd:8006)   ─┤→ OTel Collector → Mimir (metrics)
Wagtail   (Python/OTLP gRPC:4317)─┘                → Loki  (logs)
                                                    → Tempo (traces)
                                                         ↓
                                                      Grafana
```

The OTel Collector also writes JSON files to `/data/` for local inspection.

### Container Image Pattern

Each application uses multi-stage `Containerfile.*` builds with named stages:
- `wordpress` / `redmine` / `wagtail` — application stage
- `nginx` — reverse proxy sidecar stage

CI/CD (`github/workflows/`) builds and pushes to GHCR on tags matching `{product}-v{version}`.

### Kubernetes / Helm

- `kubernetes/config.yaml` — Kind cluster config (v1.34.0, ports 80/443)
- `kubernetes/helmfile.d/` — Helmfile releases: ingress-nginx, KEDA, LGTM stack
- `helm/` — Generic Helm chart (`application`) for deploying any demo app with Nginx sidecar

```bash
kind create cluster --config kubernetes/config.yaml --name demo-apps
helmfile apply   # From kubernetes/helmfile.d/
```

## Key Configuration Files

| Path | Purpose |
|------|---------|
| `etc/otel/otel-collector-config.yaml` | OTel Collector pipelines (receivers, processors, exporters, connectors) |
| `etc/grafana/datasources.yaml` | Grafana data source definitions |
| `etc/php/otel.php.ini` | PHP OTel extension settings |
| `etc/php/composer.json` | PHP OTel SDK + WordPress auto-instrumentation |
| `etc/python/requirements.txt` | Python OTel distro + OTLP exporter |
| `etc/ruby/otel.rb` | Rails initializer loading OTel SDK + all instrumentation |
| `etc/mysql/init.sql` | Database and user initialization |
| `etc/nginx/lb.conf.template` | Nginx load balancer upstream routing |
| `.envrc` | Adds `bin/` to PATH, sets `COMPOSE_PROJECT_NAME=demo` |
| `.tool-versions` | Pinned versions: kind 0.30.0, helmfile 1.1.9, helm 3.19.0 |

## OpenTelemetry Integration per App

- **WordPress (PHP):** `OTEL_PHP_AUTOLOAD_ENABLED=true` + pecl extensions (`opentelemetry`, `protobuf`) + Composer packages. Exports via OTLP HTTP.
- **Redmine (Ruby):** `etc/ruby/otel.rb` Rails initializer with `OpenTelemetry::Instrumentation::All`. Logs via Fluentd. Exports traces via OTLP.
- **Wagtail (Python):** `opentelemetry-bootstrap -a install` + `opentelemetry-instrument` wrapper. Exports via OTLP gRPC.
