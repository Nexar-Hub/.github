"""Puente fichas → OpenTodo → Horolog → propuestas de bloques. Solo pegamento.

Qué resuelve cada pieza (nada de esto reimplementa lo que ya existe):
  * Fichas del vault: fuente de verdad del proyecto (prioridad, clase, negocio,
    estado, quien, fecha límite). Se leen, nunca se escriben desde acá.
  * OpenTodo (MCP, token `agent`): tareas con estimación y energía, eventos de
    calendario, vista Día/Semana, historial, sincronización con el calendario.
  * Horolog (solo `horolog.solver.solve`, función pura): dónde cae cada bloque,
    alrededor de lo ocupado, moviendo lo mínimo respecto del plan anterior.
  * Este archivo: traduce entre los tres, marca las propuestas con la etiqueta
    `propuesta`, y guarda un lote por corrida para poder revertirla.

Protocolo de revisión (todo en la interfaz de OpenTodo, sin interfaz nueva):
  aceptar  = sacarle la etiqueta `propuesta` al bloque (queda fijo)
  editar   = arrastrarlo en Día/Semana o cambiar [time:: ] en Acciones/<ficha>.md: cuenta como
             aceptarla con tu horario (la corrida siguiente le saca `propuesta` y no la mueve)
  rechazar = ponerle la etiqueta `rechazada` (la próxima corrida lo saca del calendario y no lo vuelve a proponer)

Uso:
  planificar.py proponer   --desde 2026-11-23 --dias 5
  planificar.py replanificar --desde 2026-11-23 --dias 5   (igual que proponer; usa el plan anterior)
  planificar.py estado     --desde 2026-11-23 --dias 5
  planificar.py revertir   <lote>
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from ot_client import OT, OTError

HOROLOG = os.environ.get("HOROLOG_API_DIR")  # .../horolog/services/api, commit fijado en run_demo.sh
if HOROLOG:
    sys.path.insert(0, HOROLOG)
from horolog.domain.events import BusyInterval  # noqa: E402
from horolog.domain.intent import DailyWindow, EnergyLevel, Intent, IntentKind, Priority  # noqa: E402
from horolog.domain.plan import Plan, ScheduledBlock  # noqa: E402
from horolog.domain.time import SLOTS_PER_DAY, from_slot, to_slot  # noqa: E402
from horolog.solver.solve import solve  # noqa: E402

TZ_NAME = os.environ.get("PLAN_TZ", "America/Argentina/Buenos_Aires")
TZ = ZoneInfo(TZ_NAME)
JORNADA = (9 * 60, 19 * 60)      # horas en que se puede proponer
FOCO = (9 * 60, 13 * 60)         # [energy:: deep] solo a la mañana
P_PROP, P_RECH = "propuesta", "rechazada"
PRIORIDAD = {"ahora": 1, "siguiente": 2, "después": 3, "despues": 3}
NO_PLANIFICAR = {"bloqueado", "hecho"}
PERSONA = os.environ.get("PLAN_PERSONA", "Persona")   # valor de `quien` que ocupa tu calendario


# ---------------------------------------------------------------- fichas ----
def _front(path: Path) -> tuple[dict, str]:
    txt = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}, txt


def leer_fichas(vault: Path, acciones: str = "Acciones") -> dict[str, dict]:
    """opentodo-id del proyecto → datos de su ficha.

    `ot vault` sincroniza UNA carpeta con TODA la cuenta, así que las acciones viven en
    `Acciones/<ficha>.md` (con `ficha: "[[…]]"` en el front-matter) y la ficha sigue
    en su lugar de siempre, con su estado y prioridad. Se busca con las mismas rutas
    que director.py.
    """
    por_nombre = {}
    for pat in ["10-Empresas/*/Proyectos/*.md", "10-Empresas/*/Decisiones/*.md", "00-Contexto/Decisiones/*.md"]:
        for f in glob.glob(str(vault / pat)):
            por_nombre[Path(f).stem] = Path(f)
    fichas = {}
    for f in sorted((vault / acciones).glob("*.md")):
        fm, _ = _front(f)
        oid, enlace = fm.get("opentodo-id"), str(fm.get("ficha") or "")
        m = re.match(r"\[\[([^\]|#]+)", enlace)
        ruta = por_nombre.get(m.group(1).split("/")[-1]) if m else None
        if not oid or not ruta:
            continue
        ffm, txt = _front(ruta)
        lim = re.search(r"\*\*Fecha l[íi]mite:\*\*\s*(\d{4}-\d{2}-\d{2})", txt)
        fichas[str(oid)] = {
            "ruta": str(ruta.relative_to(vault)),
            "acciones": str(f.relative_to(vault)),
            "prioridad": str(ffm.get("prioridad", "después")),
            "clase": str(ffm.get("clase", "")),
            "estado": str(ffm.get("estado", "")),
            "quien": str(ffm.get("quien", "")),
            "negocio": str(ffm.get("negocio") or ffm.get("empresa") or ""),
            "fecha_limite": lim.group(1) if lim else None,
        }
    return fichas


def orden_negocios(vault: Path) -> list[str]:
    """En el vault real es la constante NEGOCIOS de hoy.py; acá, la línea del Plan 30-90."""
    plan = vault / "00-Contexto" / "Plan 30-90.md"
    if plan.exists():
        m = re.search(r"Prioridad de negocios:\s*(.+)", plan.read_text(encoding="utf-8"))
        if m:
            return [x.strip(" .") for x in m.group(1).split(",")]
    return []


# --------------------------------------------------------------- tiempo ----
def due_dt(due: dict | None) -> datetime | None:
    """Hora de un `due` o de un evento, en la zona del planificador.

    `date`/`time` están en la zona del propio due (`tz`); sin `tz` es hora flotante.
    (`local_*` vienen en la zona de la cuenta, no se usan: fue el primer error de la prueba.)"""
    if not due or not due.get("time"):
        return None
    tz = ZoneInfo(due["tz"]) if due.get("tz") else TZ
    return datetime.fromisoformat(f"{due['date']}T{due['time']}").replace(tzinfo=tz).astimezone(TZ)


def due_de(dt: datetime) -> dict:
    return {"date": dt.strftime("%Y-%m-%d"), "time": dt.strftime("%H:%M"), "tz": TZ_NAME}


def mismo_due(a: dict | None, b: dict | None) -> bool:
    da, db = due_dt(a), due_dt(b)
    if da or db:
        return da == db
    return (a or {}).get("date") == (b or {}).get("date")


# ---------------------------------------------------------------- lotes ----
class Lotes:
    def __init__(self, carpeta: Path):
        self.dir = carpeta
        self.dir.mkdir(parents=True, exist_ok=True)

    def todos(self) -> list[dict]:
        return [json.loads(p.read_text()) for p in sorted(self.dir.glob("*.json"))]

    def ultimo_propuesto(self) -> dict[str, dict]:
        """task_id → due que la última corrida le propuso (para detectar ediciones)."""
        out = {}
        for lote in self.todos():
            for c in lote["cambios"]:
                if lote.get("revertido"):
                    continue
                if c["despues"]["propuesta"]:
                    out[c["task_id"]] = c["despues"]["due"]
                else:
                    out.pop(c["task_id"], None)
        return out

    def guardar(self, lote: dict) -> Path:
        p = self.dir / f"{lote['id']}.json"
        p.write_text(json.dumps(lote, ensure_ascii=False, indent=2))
        return p

    def leer(self, lote_id: str) -> dict:
        return json.loads((self.dir / f"{lote_id}.json").read_text())


# ------------------------------------------------------------ planificar ---
def etiquetas(t: dict) -> list[str]:
    return list(t.get("untrusted_text", {}).get("labels") or [])


def clasificar(tareas, fichas, propuesto, ya_propuestas=frozenset()):
    """Divide las tareas abiertas en: candidatas (se pueden mover), fijas (ocupan) y avisos."""
    candidatas, fijas, avisos = [], [], []
    for t in tareas:
        labs = etiquetas(t)
        ficha = fichas.get(t.get("project_id") or "")
        dt = due_dt(t.get("due"))
        if P_RECH in labs:
            if P_PROP in labs or (t["id"] in propuesto and dt):
                avisos.append(("rechazada", t))
            continue
        if P_PROP in labs and t["id"] in propuesto and not mismo_due(t.get("due"), propuesto[t["id"]]):
            fijas.append(("editada", t))            # la persona la movió: se respeta su horario
            continue
        if dt and P_PROP not in labs:
            fijas.append(("aceptada" if t["id"] in ya_propuestas else "fija (agendada por vos)", t))
            continue
        if not ficha:
            if dt is None:
                avisos.append(("sin ficha (bandeja: aclarar antes de agendar)", t))
            continue
        if ficha["estado"] in NO_PLANIFICAR or ficha["quien"] not in (PERSONA, ""):
            continue
        if not t.get("estimate_minutes"):
            avisos.append(("sin estimación", t))
            continue
        candidatas.append((ficha, t))
    return candidatas, fijas, avisos


def prioridad_de(ficha: dict, t: dict) -> int:
    p = PRIORIDAD.get(ficha["prioridad"], 3)
    if ficha["clase"] == "crítico":
        p -= 1
    p = min(p, int(t.get("priority") or 4))
    return max(1, min(4, p))


def armar(ot: OT, vault: Path, lotes: Lotes, desde: date, dias: int):
    origen = datetime.combine(desde, datetime.min.time(), TZ)
    horizonte = dias * SLOTS_PER_DAY
    hasta = desde + timedelta(days=dias)
    fichas = leer_fichas(vault)
    negocios = orden_negocios(vault)
    propuesto = lotes.ultimo_propuesto()
    tareas = ot.all_tasks(available=True) + [
        t for t in ot.all_tasks(available=False) if P_PROP in etiquetas(t) or due_dt(t.get("due"))]
    vistas, unicas = set(), []
    for t in tareas:
        if t["id"] not in vistas and not t.get("completed"):
            vistas.add(t["id"]); unicas.append(t)
    ya = {c["task_id"] for l in lotes.todos() if not l.get("revertido") for c in l["cambios"]}
    candidatas, fijas, avisos = clasificar(unicas, fichas, propuesto, ya)

    ocupado: list[BusyInterval] = []
    ahora = datetime.now(TZ)
    if ahora > origen:                                   # nada en el pasado
        ocupado.append(BusyInterval(source_id="pasado", start_slot=0,
                                    end_slot=max(1, min(horizonte, to_slot(ahora, origen) + 1))))
    for d in range(dias):                                # fin de semana libre
        if (desde + timedelta(days=d)).weekday() >= 5:
            ocupado.append(BusyInterval(source_id="finde", start_slot=d * SLOTS_PER_DAY,
                                        end_slot=(d + 1) * SLOTS_PER_DAY))
    eventos = ot.rest("GET", f"/api/v1/calendar-feeds/events?from={desde}&to={hasta}")["events"]
    for e in eventos:
        if e.get("allDay") or e.get("free"):
            continue
        s, f = due_dt(e["start"]), due_dt(e["end"])
        if s and f and f > origen:
            ocupado.append(BusyInterval(source_id=f"evento:{e['uid']}", label=e.get("summary", ""),
                                        start_slot=max(0, to_slot(s, origen)), end_slot=max(1, to_slot(f, origen))))
    for motivo, t in fijas:
        s = due_dt(t["due"])
        f = s + timedelta(minutes=t.get("estimate_minutes") or 30)
        if f > origen and s < origen + timedelta(days=dias):
            ocupado.append(BusyInterval(source_id=f"tarea:{t['id']}", label=motivo,
                                        start_slot=max(0, to_slot(s, origen)), end_slot=to_slot(f, origen)))
    ocupado = [b for b in ocupado if b.end_slot > b.start_slot and b.start_slot < horizonte]

    intents, previo, por_iid = [], [], {}
    for ficha, t in candidatas:
        minutos = -(-int(t["estimate_minutes"]) // 15) * 15
        ventana = FOCO if (t.get("energy") == "deep") else JORNADA
        minutos = min(minutos, ventana[1] - ventana[0])
        rango = negocios.index(ficha["negocio"]) if ficha["negocio"] in negocios else 9
        iid = f"n{rango}|{t['id']}"                     # desempate de Horolog = orden de negocios
        limite = t.get("deadline") or ficha["fecha_limite"]
        due_slot = None
        if limite:
            fin = datetime.fromisoformat(limite).replace(tzinfo=TZ) + timedelta(days=1)
            due_slot = min(horizonte, max(1, to_slot(fin, origen)))
        prio = prioridad_de(ficha, t)
        intents.append(Intent(
            id=iid, kind=IntentKind.TASK, title=t["untrusted_text"]["title"], priority=Priority(prio),
            energy={"deep": EnergyLevel.HIGH, "low": EnergyLevel.LOW}.get(t.get("energy") or "", EnergyLevel.MEDIUM),
            minutes_per_period=minutos, min_chunk_minutes=minutos, max_chunk_minutes=minutos,  # 1 tarea = 1 bloque
            daily_windows=[DailyWindow(start_min=ventana[0], end_min=ventana[1])],
            due_slot=due_slot if due_slot and due_slot > minutos // 15 else None))
        por_iid[iid] = (ficha, t, prio)
        s = due_dt(t.get("due"))
        if s and P_PROP in etiquetas(t) and origen <= s < origen + timedelta(days=dias):
            st = to_slot(s, origen)
            previo.append(ScheduledBlock(intent_id=iid, occurrence=0, chunk=0, start_slot=st,
                                         end_slot=st + minutos // 15, priority=Priority(prio)))
    plan = solve(intents, ocupado, horizonte, previous=Plan(blocks=previo) if previo else None)
    return dict(plan=plan, origen=origen, por_iid=por_iid, fijas=fijas, avisos=avisos,
                eventos=eventos, ocupado=ocupado, tareas=unicas)


def aplicar(ot: OT, lotes: Lotes, r: dict, accion: str) -> dict:
    plan, origen, por_iid = r["plan"], r["origen"], r["por_iid"]
    cambios, puestos = [], set()
    for b in plan.blocks:
        ficha, t, prio = por_iid[b.intent_id]
        nuevo = due_de(from_slot(b.start_slot, origen))
        labs = etiquetas(t)
        puestos.add(t["id"])
        if mismo_due(t.get("due"), nuevo) and P_PROP in labs:
            continue
        cambios.append({"task_id": t["id"], "titulo": t["untrusted_text"]["title"], "ficha": ficha["ruta"],
                        "prioridad": prio, "base": [x for x in labs if x != P_PROP],
                        "antes": {"due": t.get("due"), "propuesta": P_PROP in labs},
                        "despues": {"due": nuevo, "propuesta": True}})
    # editadas por la persona: se aceptan con su horario (solo se saca la etiqueta)
    for motivo, t in r["fijas"]:
        if motivo == "editada":
            cambios.append({"task_id": t["id"], "titulo": t["untrusted_text"]["title"], "ficha": None, "prioridad": None,
                            "base": [x for x in etiquetas(t) if x != P_PROP],
                            "antes": {"due": t.get("due"), "propuesta": True},
                            "despues": {"due": t.get("due"), "propuesta": False}})
    # propuestas que ya no entran, y las rechazadas: salen del calendario y pierden `propuesta`
    salen = [t for (_, t, _) in por_iid.values() if t["id"] not in puestos and P_PROP in etiquetas(t)]
    salen += [t for (m, t) in r["avisos"] if m == "rechazada"]
    for t in salen:
        cambios.append({"task_id": t["id"], "titulo": t["untrusted_text"]["title"], "ficha": None, "prioridad": None,
                        "base": [x for x in etiquetas(t) if x != P_PROP],
                        "antes": {"due": t.get("due"), "propuesta": P_PROP in etiquetas(t)},
                        "despues": {"due": None, "propuesta": False}})
    lote = {"id": datetime.now(TZ).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4], "accion": accion,
            "creado": datetime.now(TZ).isoformat(timespec="seconds"), "cambios": cambios,
            "no_entra": [{"tarea": por_iid[u.intent_id][1]["untrusted_text"]["title"],
                          "faltan_min": u.shortfall_slots * 15} for u in plan.unmet],
            "solve_ms": round(plan.solve_ms, 2)}
    if not cambios:
        lote["sin_cambios"] = True
        return lote
    escribir(ot, cambios, "despues")
    lotes.guardar(lote)
    return lote


def escribir(ot: OT, cambios: list[dict], lado: str):
    por_due: dict[str, list[str]] = {}
    for c in cambios:
        if mismo_due(c["antes"]["due"], c["despues"]["due"]):
            continue                                   # solo cambia la etiqueta
        d = c[lado]["due"]
        d = {k: d[k] for k in ("date", "time", "tz") if d.get(k)} if d else None  # sin local_*
        clave = json.dumps(d, sort_keys=True)
        por_due.setdefault(clave, []).append(c["task_id"])
    for clave, ids in por_due.items():
        for i in range(0, len(ids), 50):
            ot.mcp("schedule_tasks", {"ids": ids[i:i + 50], "due": json.loads(clave)})
    upd = [{"id": c["task_id"], "labels": c["base"] + ([P_PROP] if c[lado]["propuesta"] else [])} for c in cambios]
    for i in range(0, len(upd), 50):
        ot.mcp("update_tasks", {"updates": upd[i:i + 50]})


def revertir(ot: OT, lotes: Lotes, lote_id: str, forzar=False) -> dict:
    lote = lotes.leer(lote_id)
    if lote.get("revertido"):
        return {"lote": lote_id, "ya_revertido": True}
    listos, saltados = [], []
    for c in reversed(lote["cambios"]):
        actual = ot.mcp("get_task", {"id": c["task_id"], "timezone": TZ_NAME})["task"]
        # el planificador solo es dueño de la hora y de la etiqueta `propuesta`:
        # si la persona tocó cualquiera de las dos después, no se pisa (salvo --forzar)
        igual = mismo_due(actual.get("due"), c["despues"]["due"]) and \
            (P_PROP in etiquetas(actual)) == c["despues"]["propuesta"]
        c = dict(c, base=[x for x in etiquetas(actual) if x != P_PROP])
        (listos if igual or forzar else saltados).append(c)
    if listos:
        escribir(ot, listos, "antes")
    lote["revertido"] = datetime.now(TZ).isoformat(timespec="seconds")
    lotes.guardar(lote)
    return {"lote": lote_id, "revertidos": len(listos),
            "saltados_porque_cambiaron_despues": [c["titulo"] for c in saltados]}


def estado(r: dict) -> list[dict]:
    filas = []
    for motivo, t in r["fijas"]:
        filas.append({"estado": motivo, "tarea": t["untrusted_text"]["title"], "cuando": str(due_dt(t["due"]))})
    for ficha, t, prio in r["por_iid"].values():
        if P_PROP in etiquetas(t):
            filas.append({"estado": "propuesta", "tarea": t["untrusted_text"]["title"],
                          "cuando": str(due_dt(t.get("due"))), "prioridad": prio})
    for motivo, t in r["avisos"]:
        filas.append({"estado": motivo, "tarea": t["untrusted_text"]["title"]})
    return filas


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["proponer", "replanificar", "estado", "revertir"])
    ap.add_argument("lote", nargs="?")
    ap.add_argument("--desde", default=str(date.today()))
    ap.add_argument("--dias", type=int, default=5)
    ap.add_argument("--vault", default=os.environ.get("VAULT", "."))
    ap.add_argument("--lotes", default=os.environ.get("LOTES", ".planificar/lotes"))
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args(argv)
    ot = OT(os.environ.get("OPENTODO_URL", "http://127.0.0.1:8080"), os.environ["OPENTODO_AGENT_TOKEN"])
    lotes = Lotes(Path(a.lotes))
    if a.accion == "revertir":
        out = revertir(ot, lotes, a.lote, a.forzar)
    else:
        r = armar(ot, Path(a.vault), lotes, date.fromisoformat(a.desde), a.dias)
        out = estado(r) if a.accion == "estado" else aplicar(ot, lotes, r, a.accion)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return out


if __name__ == "__main__":
    try:
        main()
    except OTError as e:
        sys.exit(f"OpenTodo: {e}")
