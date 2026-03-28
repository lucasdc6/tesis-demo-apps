"""
preprocess_script para mkslides.

Expande las directivas FILES: en un archivo markdown, fusionando los archivos
referenciados en un único deck de slides.

Uso en un archivo de slides:
    ---
    slides:
      preprocess_script: scripts/build.py
      separator: <!--s-->
    ---
    FILES: docs/parte1.md
    FILES: docs/parte2.md

Cada línea FILES: es reemplazada por el contenido del archivo referenciado.
El frontmatter del primer archivo se conserva; el de los archivos siguientes se elimina.
Los paths se resuelven relativos al directorio de trabajo (donde se ejecuta mkslides).
"""

import re
import logging
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
FILES_RE = re.compile(r"^FILES:\s+(.+)$", re.MULTILINE)
SEPARATOR_RE = re.compile(r"separator:\s*(.+)")


def _strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1).lstrip("\n")


def _get_separator(content: str) -> str:
    match = SEPARATOR_RE.search(content)
    return match.group(1).strip() if match else "<!--s-->"


def preprocess(content: str) -> str:
    file_paths = [Path(m.group(1).strip()) for m in FILES_RE.finditer(content)]

    if not file_paths:
        return content

    separator = _get_separator(content)
    frontmatter_match = FRONTMATTER_RE.match(content)
    frontmatter = frontmatter_match.group(0) if frontmatter_match else ""

    parts = []
    for i, path in enumerate(file_paths):
        logging.info(f"Found file '{path}'")
        file_content = path.read_text()
        if i > 0:
            file_content = _strip_frontmatter(file_content)
        parts.append(file_content.rstrip("\n"))

    return frontmatter + f"\n\n{separator}\n\n".join(parts) + "\n"
