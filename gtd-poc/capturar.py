"""Paso 1 y 2: idea de una nota → ficha → próximas acciones.

Aplica la regla que ya está en el vault (Operaciones.md → CAPTURAR): «una idea suelta
pasa a una ficha en Proyectos/ con prioridad: después». No usa la bandeja de OpenTodo:
la ficha es la única fuente, y `ot vault` la convierte en proyecto.

Idempotente: la línea de la nota queda con «→ [[ficha]]» y no se vuelve a capturar.
En producción el razonamiento (título, negocio, desglose en acciones) lo hace Claude en
la sesión; este script fija el resultado para que la prueba se pueda repetir.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path

PLANTILLA = """---
tipo: entregable
empresa: {negocio}
negocio: {negocio}
estado: sin empezar
prioridad: después
clase: mejora
quien: {persona}
proxima_accion: ''
depende_de: []
evidencia: ''
actualizado: {hoy}
---
# {titulo}

**Qué es:** {texto}
**Listo cuando:** (a completar al aclarar)
**Origen:** [[{nota}]]
"""


def capturar(vault: Path, nota_rel: str) -> list[Path]:
    nota = vault / nota_rel
    lineas = nota.read_text(encoding="utf-8").splitlines()
    creadas = []
    for i, l in enumerate(lineas):
        m = re.match(r"^- Idea:\s*(.+?)\s*\((\w+)\)(.*)$", l)
        if not m or "→ [[" in l:
            continue
        texto, negocio = m.group(1), m.group(2)
        titulo = texto[0].upper() + texto[1:]
        titulo = re.sub(r"^Armar un ", "", titulo).capitalize()
        ficha = vault / "10-Empresas" / negocio / "Proyectos" / f"{titulo}.md"
        if not ficha.exists():
            ficha.parent.mkdir(parents=True, exist_ok=True)
            ficha.write_text(PLANTILLA.format(negocio=negocio, persona=os.environ.get("PLAN_PERSONA", "Persona"), hoy=date.today(), titulo=titulo,
                                              texto=texto + ".", nota=nota_rel[:-3]), encoding="utf-8")
        lineas[i] = f"{l} → [[{titulo}]]"
        creadas.append(ficha)
    nota.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return creadas


def a_proyecto(vault: Path, ficha: Path, acciones: list[str], listo_cuando: str) -> Path:
    """Aclarar: sube la prioridad, define «Listo cuando» y escribe las próximas acciones
    en Acciones/<ficha>.md, la carpeta que sincroniza `ot vault`."""
    txt = ficha.read_text(encoding="utf-8")
    destino = vault / "Acciones" / ficha.name
    if destino.exists():
        return destino
    txt = txt.replace("estado: sin empezar", "estado: en curso").replace("prioridad: después", "prioridad: siguiente")
    txt = re.sub(r"proxima_accion: ''", "proxima_accion: '" + re.sub(r"\s*\[.*", "", acciones[0]) + "'", txt)
    txt = txt.replace("**Listo cuando:** (a completar al aclarar)", f"**Listo cuando:** {listo_cuando}")
    txt = txt.rstrip() + f"\n\nPróximas acciones y horarios: [[Acciones/{ficha.stem}]]\n"
    ficha.write_text(txt, encoding="utf-8")
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(f'---\nficha: "[[{ficha.stem}]]"\n---\n\nAcciones de la ficha [[{ficha.stem}]].\n\n'
                       + "\n".join(f"- [ ] {a}" for a in acciones) + "\n", encoding="utf-8")
    return destino


def secuencial(archivo: Path):
    """OpenTodo 1.6.0 ignora `opentodo-flow` en un archivo nuevo: se agrega después de la primera sincronización."""
    txt = archivo.read_text(encoding="utf-8")
    if "opentodo-flow:" not in txt:
        archivo.write_text(txt.replace("\n---\n", "\nopentodo-flow: sequential\n---\n", 1), encoding="utf-8")


if __name__ == "__main__":
    print([str(p) for p in capturar(Path(sys.argv[1]), sys.argv[2])])
