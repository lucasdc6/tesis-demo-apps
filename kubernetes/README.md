# Probando con kind

Para simplificar las pruebas se usa un cluster kind que a su vez luego
se aprovisiona con helmfile.

## Requerimientos

Para poder completar esta prueba, **deben instalarse las siguientes
herramientas**:

* [kind](https://kind.sigs.k8s.io/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* [helm](https://helm.sh/)
* [helmfile](https://helmfile.readthedocs.io/)

Además, es recomendable setear una serie de variables de ambiente que
simplifican el trabajo, no teniendo que usar más argumentos en los comandos.
Para ello, se usa [direnv](https://direnv.net/) que cargará automáticamente las
variables especificadas en el archivo `.envrc` provisto en el actual
repositorio. Si se observa el archivo mencionado, se podrá entender que las
variables seteadas son:

```
export KUBECONFIG=$PWD/.kube/config
```

Estas variables son usadas para mantener la configuración de kubernetes para
kubectl relativas a este repositorio y no interferir con otras configuraciones.
Esta variable es `KUBECONFIG` y es utilizada por kind, kubectl y helm, por lo
que es recomendable mantenerla seteada como acá se indica y de esta forma
esperar que la configuración de conexión al cluster esté en `.kube/config`.

## Creación de un cluster

Kind es una herramienta que simplifica las pruebas en un cluster k8s que correrá
en nuestra PC usando docker. La creación es muy simple, no siendo
necesario especificar una configuración como nosotros usaremos en el ejemplo
siguiente, pero es necesario realizar algunas modificaciones de las estándares:

```bash
kind create cluster --config config.yaml --name demo
```

> El comando `kind create` dejará la configuración en `$HOME/.kube/config` o en el
> archivo indicado por la variable `KUBECONFIG`. Por ello, es importante respetar
> el seteo de dicha variable como se explicó anteriormente.

El comando anterior creará un cluster con la configuración que proveemos en
`.kind/config.yaml`. Leer la configuración aclarará las razones de su
existencia. Básicamente fijamos la versión de kubernetes, y agregamos labels al
nodo control plante para poder correr le ingress controller en ese nodo como lo 
[epecifica la documentación oficial de kind](https://kind.sigs.k8s.io/docs/user/ingress/).

Al ejecutar el comando, podremos conectar con el cluster y verificar su
funcionamiento:

```
kubectl get nodes
kubectl get pods -A
```

## Instalación de las herramientas

Luego, procedemos con la instalación de las herramientas necesarias usando
helmfile. Si bien podemos directamente correr el comando explicado a
continución, es importante observar cada archivo yaml dentro de la carpeta
[`helmfile.d/`](./helmfile.d), siguiendo los valores que se van referenciando. 
Puede observarse además, que los datos sensibles del chart de argo, se manejan
de forma cifrada desde el archivo `helmfile.d/values/argocd/secrets.yaml`. Este
archivo no lo versionamos cifrado porque la idea es que cada quien utilice sus 
propias claves y datos a cifrar. Entonces el paso siguiente será el de crear
nuestra clave AGE y cifrar este archivo. Otro archivo referenciado que no
versionaremos es el `helmfile.d/values/argocd-apps/values.yaml` y la razón es
que los datos usados en el ApplicationSet dependerán del nombre de tu
repositorio.

## Recrear el cluster

Es posible destruir el cluster con

```bash
kind delete cluster --name demo
```

La recreación será únicamente con los pasos:

```bash
kind create cluster --config config.yaml --name demo
helmfile apply
```