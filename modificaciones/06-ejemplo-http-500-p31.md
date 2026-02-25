# Modificación 6 — Pág. 31: Código HTTP 501 en el ejemplo de alerta

## Problema

En la página 31, la subsección **"Ejemplo práctico basado en una alerta"** describe
un escenario donde se dispara una alerta por demasiados errores del sistema:

> "una alerta que se genera a partir de una métrica que marca la cantidad de **errores 501**
> que se genera en el sistema"

Y el diagrama debajo muestra: `errors_total{process=ABC-1, code=501}`

El código HTTP **501** corresponde a *Not Implemented* —la respuesta que un servidor
devuelve cuando no reconoce el método HTTP de la solicitud—. Es un error de cliente
específico y de muy baja frecuencia en aplicaciones web normales, por lo que rara vez
sería el código elegido para basar una alerta de volumen de errores.

El código **500** (*Internal Server Error*) o la familia **5xx** en general son los que
típicamente se monitorizan en este tipo de alertas, ya que representan errores del lado
del servidor que indican problemas en la aplicación.

## Fragmento original

> Un ejemplo práctico de estos flujos puede ser basado en una alerta que se genera a
> partir de una métrica que marca la cantidad de errores **501** que se genera en el
> sistema. Al momento de recibir la alerta, vamos a ver cuantos errores y de qué tipo
> fueron.

Diagrama: `errors_total{process=ABC-1, code=501}`

## Texto corregido

> Un ejemplo práctico de estos flujos puede ser basado en una alerta que se genera a
> partir de una métrica que marca la cantidad de errores **500** producidos por el
> sistema. Al momento de recibir la alerta, vamos a ver cuántos errores y de qué tipo
> fueron.

Diagrama: `errors_total{process=ABC-1, code=500}`

## Alternativa (más genérica)

Si se prefiere no atarse a un código específico, puede usarse la familia 5xx:

> "…la cantidad de **errores del servidor (5xx)** que se generan en el sistema…"

Y en el diagrama: `errors_total{process=ABC-1, code=~"5.."}`

## Nota

Este es un error menor que no afecta la comprensión del flujo explicado, pero que
puede generar confusión en lectores familiarizados con los códigos HTTP.
