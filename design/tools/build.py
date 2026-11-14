#!/usr/bin/env python3
"""Genera todo lo derivado del criterio desde una sola fuente: design-dna.json.

Uso (desde la raíz del repo):
    python3 design/tools/build.py                      # guia.html + tokens.css
    python3 design/tools/build.py --artifact OUT.html  # además, versión para claude.ai (sin <html>/<head>)
    python3 design/tools/build.py --skill-zip OUT.zip  # además, el zip de la skill para subir a claude.ai

Editá design-dna.json (o criterios.md) y volvé a correr esto. No hace falta tocar el HTML.
"""
import argparse
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DESIGN = ROOT / "design"
DNA = DESIGN / "design-dna.json"
TEMPLATE = DESIGN / "tools" / "guia.template.html"
SKILL_DIR = ROOT / ".claude" / "skills" / "criterio-diseno"
MARKER = "null /*__DNA__*/"


def load_dna():
    with DNA.open(encoding="utf-8") as fh:
        return json.load(fh)


def page_body(dna):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in tpl:
        raise SystemExit("La plantilla no tiene el marcador de datos " + MARKER)
    data = json.dumps(dna, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return tpl.replace(MARKER, data)


def standalone(body):
    return (
        "<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        "<!-- Archivo generado por design/tools/build.py desde design-dna.json. No editar a mano. -->\n"
        + body
        + "\n</html>\n"
    )


def tokens_css(dna):
    pal = dna["palette"]
    lines = [
        "/* Tokens del criterio de diseño. Generado por design/tools/build.py desde design-dna.json. */",
        "/* Webflow: copiá estos valores en el panel Variables. Figma: creá una colección con los mismos nombres. */",
        ":root {",
    ]
    for c in pal["base"]:
        lines.append(f"  --nx-{c['id']}: {c['hex']}; /* {c['name']} · {c['ratio']}% · {c['role']} */")
    d = pal["dark_base"]
    lines.append(f"  --nx-{d['id']}: {d['hex']}; /* {d['name']} · {d['role']} */")
    for a in pal["accents"]["options"]:
        lines.append(f"  --nx-acento-{a['id']}: {a['hex']}; /* {a['name']} · {a['use']} */")
    lines += [
        "",
        "  /* Roles: cambiá --nx-acento por el acento elegido del proyecto */",
        "  --nx-fondo: var(--nx-mejillon);",
        "  --nx-texto: var(--nx-marron);",
        "  --nx-texto-secundario: var(--nx-roca);",
        "  --nx-superficie: var(--nx-celeste);",
        "  --nx-apoyo: var(--nx-arena);",
        "  --nx-acento: var(--nx-acento-cobalto);",
        "}",
        "",
    ]
    return "\n".join(lines)


def skill_zip(out):
    files = [SKILL_DIR / "SKILL.md"] + [DESIGN / n for n in ("criterios.md", "checklist.md", "prompts.md", "design-dna.json")]
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f"criterio-diseno/{f.name}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artifact", type=pathlib.Path, help="escribe también la versión para publicar en claude.ai")
    ap.add_argument("--skill-zip", type=pathlib.Path, help="escribe también el zip de la skill")
    args = ap.parse_args()

    dna = load_dna()
    body = page_body(dna)
    (DESIGN / "guia.html").write_text(standalone(body), encoding="utf-8")
    (DESIGN / "tokens.css").write_text(tokens_css(dna), encoding="utf-8")
    print("ok  design/guia.html")
    print("ok  design/tokens.css")
    if args.artifact:
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        args.artifact.write_text(body, encoding="utf-8")
        print(f"ok  {args.artifact}")
    if args.skill_zip:
        skill_zip(args.skill_zip)
        print(f"ok  {args.skill_zip}")


if __name__ == "__main__":
    main()
