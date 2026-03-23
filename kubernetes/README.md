# Despliegue en Kubernetes

Esta carpeta contiene la configuración necesaria para desplegar la PoC de observabilidad
en un cluster de Kubernetes local usando [Kind](https://kind.sigs.k8s.io/).

El objetivo es reproducir el mismo stack de observabilidad del ambiente Docker Compose
pero en un entorno cloud-native, con las apps demo corriendo como deployments gestionados
por un Helm chart genérico.

## Qué se despliega

La infraestructura se instala con Helmfile en cinco capas:

| Helmfile | Componente | Namespace(s) | Chart(s) | Descripción |
|----------|------------|--------------|----------|-------------|
| `01-gateway-api.yaml` | Gateway API + nginx-gateway-fabric | `nginx-gateway` | `nginx/nginx-gateway-fabric` v2.4 | Gateway para exponer los servicios en `*.localhost` |
| `02-keda.yaml` | KEDA | `keda` | `kedacore/keda` v2.19 | Escalado automático basado en métricas externas |
| `03-database-operators.yaml` | Operadores de BD | `mysql-operator`, `cnpg` | `bitpoke/mysql-operator` v0.6, `cnpg/cloudnative-pg` v0.27 | Gestión de clusters MySQL y PostgreSQL |
| `04-observability.yaml` | Stack LGTM | `grafana`, `mimir`, `loki`, `tempo`, `minio`, `opentelemetry`, `kube-state-metrics` | grafana, mimir-distributed, loki, tempo-distributed, minio, otel-collector | Observabilidad completa: métricas, logs y trazas |
| `05-ganesha-nfs.yaml` | Ganesha NFS | `ganesha-nfs` | `ganesha-nfs/nfs-server-provisioner` v1.8 | Provisioner de almacenamiento NFS para PVCs compartidos |

Las aplicaciones demo (WordPress, Redmine, Wagtail) se despliegan por separado con `06-applications.yaml`:

| Release | Namespace | BD | Descripción |
|---------|-----------|----|-------------|
| `wordpress` | `wordpress` | MySQL (bitpoke/mysql-cluster) | WordPress + Nginx sidecar |
| `redmine` | `redmine` | MySQL (bitpoke/mysql-cluster) | Redmine + Nginx sidecar |
| `wagtail` | `wagtail` | PostgreSQL (CNPG) + Redis (Valkey) | Wagtail + Nginx sidecar |

## Requisitos

| Herramienta | Instalación |
|-------------|-------------|
| [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) | `go install sigs.k8s.io/kind@latest` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Gestor de paquetes del SO |
| [helm](https://helm.sh/docs/intro/install/) | `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \| bash` |
| [helmfile](https://helmfile.readthedocs.io/en/latest/#installation) | `brew install helmfile` / binario en releases |
| [sops](https://github.com/getsops/sops) | Para descifrar los secrets de los registries privados |

Todas las herramientas pueden instalarse con [asdf](https://asdf-vm.com/). Las versiones
exactas están fijadas en el archivo `.tool-versions` de la raíz del repositorio:

```bash
asdf install
```

> **KUBECONFIG**: El script guarda la configuración del cluster en `.kube/config` dentro
> de esta carpeta. Si usás [direnv](https://direnv.net/), el `.envrc` incluido configura
> la variable automáticamente al entrar al directorio.

## Crear el ambiente

El script `cluster-setup` está en `bin/` y se agrega al `PATH` mediante el `.envrc` raíz.

```bash
cluster-setup up
```

El script realiza los siguientes pasos:

1. Verifica que `kind`, `kubectl`, `helm` y `helmfile` estén instalados.
2. Crea el cluster Kind `demo-apps` con la configuración de `config.yaml`
   (Kubernetes v1.34, hostPorts 80/443, label `ingress-ready` en el nodo).
3. Instala Gateway API CRDs y nginx-gateway-fabric, y espera a que el Gateway esté listo.
4. Instala KEDA.
5. Instala los operadores de base de datos (mysql-operator y cloudnative-pg).
6. Instala el stack de observabilidad y espera a que Grafana esté disponible.
7. Instala Ganesha NFS y espera a que el provisioner esté listo.

Una vez finalizado, Grafana es accesible en **http://grafana.localhost** (acceso
anónimo con rol de administrador, sin login).

## Desplegar las apps demo

Las imágenes de las apps se publican automáticamente en el GitHub Container Registry
cuando se crea un tag con el formato `<app>-v<versión>` (por ejemplo `wordpress-v1.0.0`).
Cada app genera dos imágenes: una para la aplicación y otra para el sidecar NGINX.

```
ghcr.io/<usuario>/<repo>/wordpress/app:<versión>
ghcr.io/<usuario>/<repo>/wordpress/nginx:<versión>
ghcr.io/<usuario>/<repo>/redmine/app:<versión>
ghcr.io/<usuario>/<repo>/redmine/nginx:<versión>
ghcr.io/<usuario>/<repo>/wagtail/app:<versión>
ghcr.io/<usuario>/<repo>/wagtail/nginx:<versión>
```

Las credenciales del registry se manejan como secrets cifrados con SOPS. Para desplegar
las apps usá el helmfile de aplicaciones desde el directorio `kubernetes/`:

```bash
cd kubernetes/
helmfile --file helmfile.d/06-applications.yaml apply
```

## Verificar el estado

```bash
cluster-setup status
```

Muestra los nodos, pods de todos los namespaces y los ingresses activos.

## URLs de acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Grafana | http://grafana.localhost | N/A (acceso anónimo) |
| WordPress | http://wordpress.localhost *(si se desplegó)* | admin / admin |
| Redmine | http://redmine.localhost *(si se desplegó)* | admin / admin |
| Wagtail | http://wagtail.localhost *(si se desplegó)* | admin / changeme |

> Los dominios `*.localhost` se resuelven localmente sin necesidad de modificar
> `/etc/hosts` en Linux. En macOS puede ser necesario agregar las entradas manualmente.

## Destruir el ambiente

```bash
cluster-setup down
```

Elimina el cluster Kind `demo-apps` y todos sus recursos. La carpeta `.kube/` con la
configuración del cluster también puede borrarse manualmente.

## Estructura de la carpeta

```
kubernetes/
├── config.yaml            # Configuración del cluster Kind (versión k8s, puertos, labels)
├── .envrc                 # Configura KUBECONFIG y SOPS_AGE_RECIPIENTS para direnv
├── charts/
│   └── gateway-api-crd/   # Chart local con los CRDs de Gateway API (kustomize)
└── helmfile.d/
    ├── bases/
    │   └── repositories.yaml       # Repositorios Helm compartidos entre helmfiles
    ├── 01-gateway-api.yaml         # Helm release: Gateway API CRDs + nginx-gateway-fabric
    ├── 02-keda.yaml                # Helm release: KEDA
    ├── 03-database-operators.yaml  # Helm releases: mysql-operator y cloudnative-pg
    ├── 04-observability.yaml       # Helm releases: grafana, mimir, loki, tempo, minio, otel-collector
    ├── 05-ganesha-nfs.yaml         # Helm release: nfs-server-provisioner
    ├── 06-applications.yaml        # Helm releases: wordpress, redmine, wagtail (+ sus BDs)
    └── values/                     # Archivos de valores por release
```

## Helm chart de las apps (`../helm/`)

El chart en `../helm/` es genérico: puede desplegar cualquiera de las tres apps.
Cada release genera un Deployment con dos contenedores (app + nginx sidecar), un
Service ClusterIP, un HTTPRoute (Gateway API) y opcionalmente un PVC para archivos persistentes.

Los valores principales a configurar por app son:

| Valor | Descripción |
|-------|-------------|
| `app.image.repository` / `app.image.tag` | Imagen de la aplicación |
| `nginx.image.repository` / `nginx.image.tag` | Imagen del sidecar NGINX |
| `app.port` | Puerto interno de la app (PHP-FPM: 9000, Rails: 3000, uWSGI: 8000) |
| `app.staticDir` | Ruta de los estáticos dentro del contenedor (se copian al sidecar) |
| `app.fileDir` | Ruta de los archivos subidos (mapeada al PVC si `persistence.enabled=true`) |
| `app.env` | Variables de entorno (configmap) |
| `app.secretEnv` | Variables de entorno sensibles (secret) |
| `ingress.hosts` | Hostname del HTTPRoute |
| `persistence.enabled` / `persistence.size` | Habilitar PVC para archivos persistentes |
