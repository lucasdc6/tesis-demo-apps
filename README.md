# Aplicaciones demo

En este repositorio se van a encontrar todos los archivos usados para realizar
las pruebas de la tesis "Observabilidad, una base para aplicaciones resilientes"

## Requerimeintos

Para poner en funcionamiento las demos, es necesario contar con

- docker
- docker compose

## Iniciar ambiente

El ambiente de las pruebas se encuentra dividido en diferentes archivos
`docker compose`

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
docker compose up
# O alternativamente se puede enviar la ejecución al background
docker compose up -d
```

Luego, podemos levantar las demo ejecutando

```bash
docker compose -f docker-compose.<DEMO>.yaml up -d

# Por ejemplo, para levantar wordpress
docker compose -f docker-compose.wordpress.yaml up -d
```

Alternmativamente, podemos ejecutar todos los servicios con un solo comando

```bash
docker compose \
  -f docker-compose.yaml \
  -f docker-compose.wordpress.yaml \
  -f docker-compose.redmine.yaml \
  -f docker-compose.wagtail.yaml \
  up
```
> Recordar que se puede enviar al background usando el flag `-d`

Luego, para eliminar todos los recursos creados por docker, ejecutar

```bash
docker compose \
  -f docker-compose.yaml \
  -f docker-compose.wordpress.yaml \
  -f docker-compose.redmine.yaml \
  -f docker-compose.wagtail.yaml \
  down -v
```

> Notar que el flag `-v` va a borrar los volumenes

## Inspeccionar el ambiente

Una vez levantado el ambiente, podemos acceder a las siguientes URLs

- http://grafana.localhost
- http://wordpress.localhost
- http://redmine.localhost
- http://wagtail.localhost