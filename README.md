# Aplicaciones demo

En este repositorio se van a encontrar todos los archivos usados para realizar
las pruebas de la tesis "Observabilidad, una base para aplicaciones resilientes"

## Requerimeintos

Para poner en funcionamiento las demos, es necesario contar con

- docker
- docker compose

## Iniciar ambiente

El ambiente de las pruebas se encuentra dividido en diferentes archivos
`docker compose` que se pueden encontrar en el directorio `compose_files`

- `docker-compose.yaml`: Archivo principal que cuenta con todos los servicios
  base necesarios para la ejecución de las pruebas, tales como
  - Una base de datos `mysql`.
  - Un `nginx` que funciona a modo de reverse proxy para simplificar el acceso a
    los servicios.
  - Un colector de `opentelemetry` que va a recibir todos los datos y los va a
    insertar en la base de datos adecuada.
  - Un `grafana` que va a permitir visualizar la información.
  - Una base de datos `mimir` para almacenar métricas.
  - Una base de datos `loki` para almacenar logs, junto a un servicio para
    configurar los permisos de su filesystem.
  - Una base de datos `tempo` para almacenar trazas, junto a un servicio para
    configurar los permisos de su filesystem.
- `docker-compose.wordpress.yaml`: Archivo del servicio `wordpress`, cuenta con
  2 servicios, el principal que levanta un `php-fpm` y un `nginx` que sirve
  tanto los estáticos y que envía todos los requerimientos php al servicio de
  `wordpress` mediante el protocolo `fastcgi`.
- `docker-compose.redmine.yaml`: Archivo del servicio de `redmine`, cuenta con 2
  servicios, el principal que levanta un application server `puma`, y un `nginx`
  que sirve tanto los estáticos y proxea los requerimeintos de `redmine` al
  servidor `puma` mediante `proxy_pass`.
- `docker-compose.wagtail.yaml`: Archivo del servicio de `wagtail`, cuenta con 2
  servicios, el principal que levanta un application server `uWSGI`, y un `nginx`
  que sirve tanto los estáticos y proxea los requerimeintos de `wagtail` al
  servidor `uWSGI` mediante `proxy_pass`.

Para iniciar los servicios base, ejecutar

```bash
./bin/service-run base
```

Luego, podemos levantar las demo ejecutando

```bash
./bin/service-run <DEMO>

# Por ejemplo, para levantar wordpress
./bin/service-run wordpress
```

Alternmativamente, podemos ejecutar todos los servicios con un solo comando

```bash
./bin/service-run all
```

Luego, para eliminar todos los recursos creados por docker, ejecutar

```bash
./bin/service-stop all
```

> Notar que el flag `-v` va a borrar los volumenes

## Inspeccionar el ambiente

Una vez levantado el ambiente, podemos acceder a las siguientes URLs

- http://grafana.localhost
- http://wordpress.localhost
- http://redmine.localhost
- http://wagtail.localhost