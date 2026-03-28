# Slides

Presentación generada con [mkslides](https://github.com/bharel/mkslides) (Reveal.js).

## Estructura

```
slides/
├── scripts
│   └── build.py      # Script de preprocesamiento (fusión de archivos)
├── mkslides.yml      # Configuración global
├── docs/
│   ├── index.md      # Punto de entrada: lista los archivos con FILES:
│   ├── parte1.md     # Sección 1
│   └── parte2.md     # Sección 2
└── site/             # Output generado (ignorado en git)
```

## Dependencias

Requiere [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Uso

### Servir en modo desarrollo

```bash
uv run mkslides serve
```

### Generar sitio estático

```bash
uv run mkslides build
```

El sitio queda en `site/`.

## Agregar slides

Las slides se organizan en archivos separados y se combinan mediante el script `build.py`.

**`docs/index.md`** — archivo de entrada, solo referencia otros archivos:

```markdown
---
slides:
  separator: <!--s-->
  theme: solarized
---
FILES: docs/intro.md
FILES: docs/capitulo1.md
FILES: docs/capitulo2.md
```

Cada archivo referenciado es un archivo markdown normal donde los slides se separan con `<!--s-->`:

```markdown
---
slides:
  theme: solarized
---

# Título del capítulo

<!--s-->

## Segunda slide

Contenido...
```

Solo el primer archivo conserva su frontmatter YAML; el resto se fusiona automáticamente.
