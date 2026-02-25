# Modificación 1 — Pág. 35: "Correlación entre tableros" (sección vacía)

## Problema

En la página 35, bajo la subsección **"Correlación entre tableros"**, el título aparece
en el documento (y en el índice, pág. 2) pero no hay ningún párrafo de contenido.
La sección siguiente que tiene texto es "Factores sobre el almacenamiento de datos"
(pág. 35), lo que confirma que el cuerpo de esta subsección quedó sin redactar.

## Texto sugerido

> A diferencia de la correlación entre señales —que permite navegar de métricas a trazas
> o de trazas a logs dentro de un mismo evento—, la correlación entre tableros opera a un
> nivel superior: permite vincular distintos paneles de Grafana de forma que el usuario
> pueda transitar desde una vista de alto nivel hacia una vista de mayor detalle, o desde
> la perspectiva del servicio hacia la perspectiva de la infraestructura.
>
> Grafana ofrece dos mecanismos principales para implementar esta navegación. El primero
> son los *data links*, que permiten adjuntar a cualquier punto de un panel un enlace que
> abre otro tablero pasando el valor del punto como parámetro. Por ejemplo, al hacer clic
> sobre el pico de latencia de un servicio en un gráfico de series de tiempo, es posible
> navegar automáticamente hacia el tablero de trazas de ese servicio filtrado en el
> instante de tiempo exacto donde ocurrió el evento.
>
> El segundo mecanismo son los *dashboard links*, que asocian tableros entre sí mediante
> variables compartidas. Cuando un tablero declara una variable —como el nombre del
> servicio o el entorno de despliegue—, esa variable puede propagarse al tablero de
> destino, garantizando que ambas vistas reflejen el mismo contexto. Esta técnica permite
> construir jerarquías de tableros: un tablero ejecutivo que muestra el estado global del
> sistema, un tablero operacional por servicio con métricas RED, y un tablero de
> infraestructura con métricas USE para los recursos subyacentes, todos navegables de
> forma coherente.
>
> La correlación entre tableros es especialmente valiosa durante la investigación de
> incidentes, ya que reduce el tiempo necesario para transitar entre las distintas
> perspectivas del sistema —desde el síntoma visible hasta la causa raíz— sin perder el
> contexto temporal del evento bajo análisis.

## Ubicación exacta en el documento

Insertar este texto inmediatamente después del título **"Correlación entre tableros"**
(pág. 35), antes de la sección **"Factores sobre el almacenamiento de datos"**.
