# Conclusiones

## Cumplimiento del objetivo

El objetivo central de esta tesina fue identificar los marcos de trabajo necesarios para comprender y reconocer el desempeño de los sistemas en ambientes productivos, de forma agnóstica a la tecnología, con el fin de anticipar problemas, determinar cuándo escalar un servicio y reducir el tiempo de diagnóstico ante incidentes. La prueba de concepto desarrollada permite afirmar que dicho objetivo fue alcanzado.

Se demostró que es posible instrumentar tres aplicaciones preexistentes —desarrolladas en lenguajes y frameworks distintos (PHP, Ruby on Rails y Python/Django)— sin modificar su código fuente, centralizando sus señales de telemetría en un stack de observabilidad unificado basado en herramientas de código abierto. La PoC fue desplegada en dos entornos complementarios: un ambiente local con Docker Compose, orientado al ciclo de desarrollo e inspección de trazas, y un cluster de Kubernetes local (Kind), en el que se demostró el escalado automático de los servicios impulsado por las propias métricas derivadas de las trazas.

---

## Sobre los pilares de la observabilidad

La tesis profundizó en los tres pilares fundamentales de la observabilidad —métricas, registros y trazas— y su análisis revela que ninguno resulta suficiente de forma aislada. Las métricas permiten conocer el estado agregado del sistema a lo largo del tiempo y son el insumo principal para alertas y decisiones de escalado; los registros aportan el detalle de los eventos discretos que ocurren en la aplicación; y las trazas distribuidas exponen el flujo completo de un requerimiento a través de todos los componentes involucrados.

El verdadero valor de la observabilidad emerge cuando estas tres señales pueden correlacionarse. La correlación basada en identificadores de requerimiento —`trace_id` y `span_id`— permite navegar desde una alerta en un dashboard de métricas hasta la traza del requerimiento afectado, y desde allí hasta los registros exactos emitidos durante su procesamiento. Este flujo de trabajo reduce significativamente el tiempo medio de resolución de incidentes (MTTR), que es uno de los indicadores más relevantes para evaluar la resiliencia operativa de un sistema.

---

## Sobre OpenTelemetry como estándar unificador

Uno de los hallazgos más relevantes de esta investigación es la consolidación de OpenTelemetry como el estándar de facto para la instrumentación de aplicaciones en entornos cloud-native. Antes de su surgimiento, la fragmentación entre herramientas propietarias (Zipkin, Jaeger, Prometheus, sistemas de logging heterogéneos) obligaba a los equipos a adoptar una solución por cada señal, generando acoplamiento con proveedores específicos y dificultando la portabilidad de la infraestructura de observabilidad.

OpenTelemetry resuelve esta problemática al ofrecer:

- Un protocolo de transporte unificado (OTLP) para las tres señales.
- SDKs para los principales lenguajes de programación, con distintos niveles de madurez.
- Instrumentación automática para frameworks populares, que elimina la necesidad de modificar el código fuente de las aplicaciones.
- Un componente intermediario —el OTel Collector— que desacopla la recolección del almacenamiento, permitiendo cambiar los backends sin tocar las aplicaciones.

La adopción de OTLP por parte de GrafanaLabs en noviembre de 2023 y su incorporación por New Relic y Datadog confirman que el estándar trasciende el ecosistema de código abierto y se proyecta como la interfaz universal de la telemetría en la industria.

---

## Sobre el stack LGTM como alternativa open-source

El stack compuesto por Loki, Grafana, Tempo y Mimir demostró ser una alternativa viable y completa a soluciones comerciales para la centralización de las tres señales de observabilidad. Cada componente está optimizado para su dominio específico:

- **Mimir** ofrece almacenamiento de métricas compatible con la API de Prometheus, con soporte para alta cardinalidad y retención configurable.
- **Loki** adopta un modelo de indexado basado exclusivamente en etiquetas, reduciendo el costo de almacenamiento en comparación con soluciones que indexan el contenido completo de los logs.
- **Tempo** almacena trazas de forma eficiente, con integración nativa con Grafana para la navegación desde métricas y logs hacia trazas específicas.
- **Grafana** unifica la visualización de las tres señales en un único panel, habilitando la correlación interactiva entre dashboards.

Un aporte significativo de la arquitectura implementada es el uso del conector `spanmetrics` del OTel Collector, que deriva métricas RED (Tasa, Errores, Duración) directamente a partir de las trazas, sin requerir instrumentación adicional. Esto permite contar con métricas orientadas al servicio desde el primer momento en que se habilita la instrumentación de trazas.

---

## Sobre la instrumentación de aplicaciones heterogéneas

La PoC demostró que el ecosistema de OpenTelemetry presenta distintos niveles de madurez según el lenguaje y el tipo de señal:

**Python** ofrece el mayor nivel de automatización: el comando `opentelemetry-instrument` actúa como wrapper del proceso de la aplicación, inyectando la instrumentación en tiempo de ejecución sin ninguna modificación en el código. Es la estrategia con menor fricción de adopción.

**PHP** requiere instalar una extensión de bajo nivel vía PECL y configurar la directiva `auto_prepend_file` en el servidor, pero una vez configurado, opera de forma completamente transparente para el código de la aplicación. La instrumentación abarca el ciclo de vida completo de la petición HTTP y las consultas a la base de datos.

**Ruby** es el caso más complejo: si bien el SDK permite instrumentar frameworks como Rails mediante un inicializador, el soporte para la exportación de logs vía OTLP no estaba disponible en el momento de la implementación. Esto requirió incorporar Fluentd como agente de recolección de logs, configurando el logger de Rails para que emita en formato JSON estructurado con los campos `trace_id` y `span_id`. De este modo se preserva la correlación entre logs y trazas, aunque a costa de una mayor complejidad operativa.

La diversidad de estrategias requeridas ilustra una conclusión importante: la instrumentación de aplicaciones preexistentes no sigue un camino único, y la elección de la estrategia adecuada depende del lenguaje, el framework y el estado de madurez del SDK correspondiente. Sin embargo, en todos los casos fue posible instrumentar las aplicaciones sin alterar su lógica de negocio.

---

## Sobre las prácticas recomendadas y la metodología Twelve-Factor

La contenerización de las aplicaciones siguiendo los principios de la metodología Twelve-Factor App demostró ser un habilitador clave de la observabilidad. En particular:

- **Factor III (Configuración en tiempo de ejecución)**: toda la configuración de OpenTelemetry se inyecta mediante variables de entorno (`OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES`), lo que permite adaptar el comportamiento de la instrumentación por ambiente sin reconstruir las imágenes.
- **Factor XI (Registros como flujos de eventos)**: configurar las aplicaciones para escribir sus logs a la salida estándar simplifica enormemente la recolección centralizada, ya sea por el daemon de Docker o por el agente de Fluentd.
- **Factor VI (Procesos sin estado)**: las aplicaciones stateless pueden escalarse horizontalmente sin fricción; la observabilidad es el mecanismo que permite determinar cuándo ese escalado es necesario.

La adopción conjunta de estas prácticas reduce la barrera para incorporar observabilidad desde las etapas tempranas del ciclo de vida del software, en lugar de tratarla como una preocupación post-despliegue.

---

## Sobre la observabilidad como base para la resiliencia

El título de esta tesina establece una relación causal entre observabilidad y resiliencia que los resultados de la investigación permiten fundamentar. Una aplicación resiliente debe ser capaz de adaptarse ante eventos inesperados —picos de carga, fallos parciales, degradación de dependencias— sin que el servicio se interrumpa para sus usuarios.

Sin embargo, la adaptación automática solo es posible si el sistema tiene visibilidad sobre su propio estado. Es esta visibilidad la que habilita:

- **El escalado automático basado en métricas**: en la implementación Kubernetes de la PoC, KEDA fue configurado para escalar cada Deployment en función de la tasa de peticiones almacenada en Mimir, derivada automáticamente por el conector `spanmetrics` del OTel Collector a partir de las trazas. Un recurso `ScaledObject` por aplicación consulta esta métrica vía la API de Prometheus de Mimir y, cuando supera el umbral configurado por réplica activa, KEDA ordena al scheduler de Kubernetes aumentar el número de réplicas. Al ejecutar la prueba de carga con Locust —incrementando usuarios concurrentes a razón de 5 por segundo hasta 50—, el aumento de la tasa de peticiones fue inmediatamente visible en Grafana; pasados los segundos de evaluación, el sistema escaló de 1 a 4 réplicas y la latencia promedio retornó a los niveles basales. Al finalizar la carga, el período de enfriamiento (`cooldownPeriod`) permitió la reducción ordenada a una sola réplica. Este ciclo demostró en la práctica que las señales de observabilidad pueden actuar como insumo directo de mecanismos de resiliencia, sin intervención humana.
- **La detección temprana de anomalías**: las trazas distribuidas exponen cuellos de botella en operaciones específicas (consultas lentas a la base de datos, dependencias externas degradadas), permitiendo actuar antes de que el problema sea visible para los usuarios finales.
- **La reducción del tiempo de diagnóstico**: la correlación entre las tres señales permite que un operador, ante una alerta de latencia elevada, pueda navegar hasta la traza exacta que originó el problema y, desde allí, acceder a los logs del proceso en cuestión. Lo que antes podía requerir horas de análisis manual se reduce a minutos.

La analogía del parabrisas lleno de barro, citada en la introducción, resulta especialmente apropiada: operar un sistema en producción sin observabilidad equivale a conducir sin visibilidad. La observabilidad no elimina los incidentes, pero proporciona las herramientas para comprenderlos, contenerlos y prevenirlos.

---

## Limitaciones y líneas de trabajo futuras

La presente implementación, si bien alcanza los objetivos planteados, presenta limitaciones que abren líneas de trabajo futuras:

- **Soporte de logs OTLP en Ruby**: el SDK de Ruby para OpenTelemetry no ofrecía, al momento de la implementación, exportación nativa de logs vía OTLP. A medida que el SDK madure, la dependencia de Fluentd podrá eliminarse, simplificando la arquitectura.

- **Monitoreo de caja negra**: la arquitectura implementada cubre únicamente el monitoreo de caja blanca, que requiere acceso a la infraestructura donde se despliegan los servicios. La incorporación de pruebas sintéticas (caja negra) —verificando el comportamiento del sistema desde la perspectiva del usuario final, incluso desde ubicaciones geográficas distribuidas— complementaría el panorama de observabilidad con una perspectiva exterior.

- **Definición de SLOs y presupuestos de error**: la tesina describe la importancia de los Objetivos de Nivel de Servicio (SLOs) y los presupuestos de error en la ingeniería de confiabilidad de sitios (SRE), pero su definición y monitoreo activo no fueron implementados en la PoC. Una extensión natural sería definir SLOs basados en las métricas RED derivadas por el conector `spanmetrics` y configurar alertas automáticas sobre el presupuesto de error.

- **Integración con service mesh**: la incorporación de un service mesh como Istio o Linkerd permitiría obtener trazas y métricas de red a nivel de infraestructura, sin ningún cambio en las aplicaciones, complementando la observabilidad de caja blanca con visibilidad sobre la comunicación entre servicios.

- **Rollbacks automáticos basados en observabilidad**: una extensión lógica de la arquitectura sería integrar las métricas de observabilidad con el pipeline de despliegue continuo, habilitando rollbacks automáticos ante degradaciones detectadas en las métricas de error o latencia luego de un despliegue.

---

## Reflexión final

La observabilidad no es un producto que se instala, sino una disciplina que se construye a lo largo del ciclo de vida del software. Requiere decisiones en el diseño de las aplicaciones, en su instrumentación, en la arquitectura de recolección y almacenamiento de datos, y en la cultura del equipo que los interpreta y actúa en consecuencia.

Esta tesina buscó demostrar que instrumentar aplicaciones heterogéneas con OpenTelemetry y centralizar sus señales en un stack de observabilidad unificado es una tarea alcanzable, incluso sobre aplicaciones preexistentes y sin acceso a su código fuente. El resultado es un sistema capaz de responder, con evidencia empírica, a las preguntas más críticas para la operación de servicios en producción: qué está fallando, dónde está fallando, por qué está fallando y cómo ha evolucionado el comportamiento del sistema a lo largo del tiempo.

Esa capacidad de respuesta es, en última instancia, la base sobre la que se construye la resiliencia.
