# Despliegue en Kubernetes

Esta carpeta contiene la configuración necesaria para desplegar la PoC de observabilidad
en un cluster de Kubernetes local usando [Kind](https://kind.sigs.k8s.io/).

El objetivo es reproducir el mismo stack de observabilidad del ambiente Docker Compose
pero en un entorno cloud-native, con las apps demo corriendo como deployments gestionados
por un Helm chart genérico.

## Qué se despliega

El script `cluster-setup` crea el cluster e instala tres componentes de infraestructura
mediante Helmfile:

| Componente | Namespace | Chart | Descripción |
|------------|-----------|-------|-------------|
| ingress-nginx | `ingress-nginx` | `ingress-nginx/ingress-nginx` v4.10 | Ingress controller para exponer los servicios en `*.localhost` |
| KEDA | `keda` | `kedacore/keda` v2.18 | Escalado automático basado en métricas externas |
| LGTM Distributed | `observability` | `grafana/lgtm-distributed` v2.1 | Stack completo: Loki + Grafana + Tempo + Mimir |

Las aplicaciones demo (WordPress, Redmine, Wagtail) se despliegan por separado usando el
Helm chart genérico ubicado en [`../helm/`](../helm/).

## Requisitos

| Herramienta | Instalación |
|-------------|-------------|
| [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) | `go install sigs.k8s.io/kind@latest` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Gestor de paquetes del SO |
| [helm](https://helm.sh/docs/intro/install/) | `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \| bash` |
| [helmfile](https://helmfile.readthedocs.io/en/latest/#installation) | `brew install helmfile` / binario en releases |

> **KUBECONFIG**: El script guarda la configuración del cluster en `.kube/config` dentro
> de esta carpeta. Si usás [direnv](https://direnv.net/), el `.envrc` incluido configura
> la variable automáticamente al entrar al directorio.

## Crear el ambiente

```bash
cd kubernetes/
./cluster-setup up
```

El script realiza los siguientes pasos:

1. Verifica que `kind`, `kubectl`, `helm` y `helmfile` estén instalados.
2. Crea el cluster Kind `demo-apps` con la configuración de `config.yaml`
   (Kubernetes v1.34, hostPort 80/443, label `ingress-ready` en el nodo).
3. Instala ingress-nginx y espera a que esté listo.
4. Instala KEDA.
5. Instala el stack LGTM distribuido y espera a que Grafana esté disponible.

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

Para desplegar una app, usá el chart en `../helm/` pasando los valores específicos:

```bash
# Ejemplo: desplegar Wagtail
helm upgrade --install wagtail ../helm/ \
  --namespace demo-apps --create-namespace \
  --set app.image.repository=ghcr.io/<usuario>/<repo>/wagtail/app \
  --set app.image.tag=<versión> \
  --set nginx.image.repository=ghcr.io/<usuario>/<repo>/wagtail/nginx \
  --set nginx.image.tag=<versión> \
  --set app.port=8000 \
  --set app.staticDir=/app/bakerydemo/static \
  --set app.fileDir=/app/bakerydemo/media \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set "ingress.hosts[0].host=wagtail.localhost" \
  --set "ingress.hosts[0].paths[0].path=/" \
  --set "ingress.hosts[0].paths[0].pathType=Prefix"
```

> Las variables de entorno específicas de cada app (credenciales de base de datos,
> endpoints de OTel, etc.) se pasan vía `--set app.env.<VAR>=<valor>` o mediante
> un archivo de valores `-f values-wagtail.yaml`.

## Verificar el estado

```bash
./cluster-setup status
```

Muestra los nodos, pods de todos los namespaces y los ingresses activos.

## URLs de acceso

| Servicio | URL |
|----------|-----|
| Grafana | http://grafana.localhost |
| WordPress | http://wordpress.localhost *(si se desplegó)* |
| Redmine | http://redmine.localhost *(si se desplegó)* |
| Wagtail | http://wagtail.localhost *(si se desplegó)* |

> Los dominios `*.localhost` se resuelven localmente sin necesidad de modificar
> `/etc/hosts` en Linux. En macOS puede ser necesario agregar las entradas manualmente.

## Destruir el ambiente

```bash
./cluster-setup down
```

Elimina el cluster Kind `demo-apps` y todos sus recursos. La carpeta `.kube/` con la
configuración del cluster también puede borrarse manualmente.

## Estructura de la carpeta

```
kubernetes/
├── cluster-setup          # Script de gestión del cluster (up / down / status)
├── config.yaml            # Configuración del cluster Kind (versión k8s, puertos, labels)
├── .envrc                 # Configura KUBECONFIG para direnv
└── helmfile.d/
    ├── 01-ingress-nginx.yaml   # Helm release: ingress-nginx
    ├── 02-keda.yaml            # Helm release: KEDA
    ├── 03-observability.yaml   # Helm release: lgtm-distributed
    └── values/
        ├── ingress-nginx.yaml  # hostPort habilitado, nodeSelector ingress-ready
        ├── keda.yaml           # (valores por defecto)
        └── lgtm-distributed.yaml  # Grafana con ingress y acceso anónimo habilitado
```

## Helm chart de las apps (`../helm/`)

El chart en `../helm/` es genérico: puede desplegar cualquiera de las tres apps.
Cada release genera un Deployment con dos contenedores (app + nginx sidecar), un
Service ClusterIP, un Ingress y opcionalmente un PVC para archivos persistentes.

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
| `ingress.hosts` | Hostname del ingress |
| `persistence.enabled` / `persistence.size` | Habilitar PVC para archivos persistentes |
