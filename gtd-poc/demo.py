"""Los 8 pasos de la prueba, con chequeos. Lo llama run_demo.sh después de levantar todo.

Actores:
  claude  = token `agent` (MCP): lo que haría Claude. Sus cambios quedan como «AI assistant».
  persona = token `full` (REST) y edición de archivos: lo que haría la persona en la app o en Obsidian.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import caldav

import capturar
import planificar
from ot_client import OT

TZ = ZoneInfo("America/Argentina/Buenos_Aires")
WORK, VAULT, B = Path(os.environ["WORK"]), Path(os.environ["VAULT"]), os.environ["B"]
EV = WORK / "evidencia"
claude = OT(B, os.environ["OPENTODO_AGENT_TOKEN"])
persona = OT(B, os.environ["OPENTODO_FULL_TOKEN"])
SEMANA = date(2026, 11, 23)
ACC = VAULT / "Acciones"              # la única carpeta de `ot vault` (sincroniza toda la cuenta)
CARPETAS = [ACC]
NOTA = "Diario/2026-11-21.md"
CHEQUEOS: list[dict] = []


# ------------------------------------------------------------------ util ----
def paso(n, t):
    print(f"\n=== {n}. {t}", flush=True)


def check(paso_n, nombre, ok, detalle=""):
    CHEQUEOS.append({"paso": paso_n, "chequeo": nombre, "ok": bool(ok), "detalle": detalle})
    print(f"  {'OK ' if ok else 'FALLA'} {nombre}" + (f" — {detalle}" if detalle else ""), flush=True)


def guardar(nombre, data):
    (EV / f"{nombre}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def ot(*args) -> str:
    p = subprocess.run([os.environ["OT_BIN"], *args], capture_output=True, text=True)
    return (p.stdout + p.stderr).strip()


def foto(nombre, ruta, modo=""):
    p = subprocess.run(["node", "capturas.mjs", nombre, ruta] + ([modo] if modo else []),
                       capture_output=True, text=True, env=os.environ)
    if p.returncode:
        print("  (captura falló)", p.stderr[-600:])
    return p.returncode == 0


def plan(*args):
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return planificar.main(list(args))


def tareas():
    return claude.all_tasks()


def con_hora(ts):
    return [t for t in ts if planificar.due_dt(t.get("due"))]


def propuestas():
    return [t for t in tareas() if "propuesta" in planificar.etiquetas(t)]


def solapa(t, eventos):
    s = planificar.due_dt(t["due"])
    f = s + timedelta(minutes=t.get("estimate_minutes") or 30)
    for e in eventos:
        es, ef = planificar.due_dt(e["start"]), planificar.due_dt(e["end"])
        if es and ef and not e.get("free") and s < ef and es < f:
            return e["summary"]
    return None


# --------------------------------------------------------------- caldav ----
dav = caldav.DAVClient(url="http://127.0.0.1:5232/persona/", username="persona", password="sandbox-pass")


def cal(cid, nombre):
    for c in dav.principal().calendars():
        if c.url.path.rstrip("/").endswith(cid):
            return c
    return dav.principal().make_calendar(name=nombre, cal_id=cid)


def evento(c, uid, titulo, ini, fin, rrule=None):
    r = f"RRULE:{rrule}\r\n" if rrule else ""
    c.save_event("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//demo//ES\r\nBEGIN:VEVENT\r\n"
                 f"UID:{uid}@sandbox\r\nDTSTAMP:20261121T120000Z\r\n"
                 f"DTSTART;TZID=America/Argentina/Buenos_Aires:{ini}\r\n"
                 f"DTEND;TZID=America/Argentina/Buenos_Aires:{fin}\r\n{r}SUMMARY:{titulo}\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")


def eventos_caldav(c):
    out = []
    for e in c.events():
        v = e.icalendar_component
        out.append({"uid": str(v.get("uid")), "titulo": str(v.get("summary")),
                    "inicio": v.decoded("dtstart").isoformat(), "fin": v.decoded("dtend").isoformat()})
    return out


CONN = {}


def sync_cal(esperar_hasta=None):
    """«Sincronizar ahora» de la conexión y esperar a que termine."""
    cid = CONN["id"]
    antes = persona.rest("GET", "/api/v1/calendar-sync/connections")["connections"][0].get("last_sync_at")
    persona.rest("POST", f"/api/v1/calendar-sync/connections/{cid}/sync")
    for _ in range(80):
        c = persona.rest("GET", "/api/v1/calendar-sync/connections")["connections"][0]
        if c.get("last_sync_at") and c.get("last_sync_at") != antes and c["state"] not in ("waiting", "pending"):
            if esperar_hasta is None or esperar_hasta():
                return c
        time.sleep(0.5)
    return c


def eventos_ot(desde, hasta):
    return claude.rest("GET", f"/api/v1/calendar-feeds/events?from={desde}&to={hasta}")["events"]


def label_ids():
    return {l["name"]: l["id"] for l in persona.rest("GET", "/api/v1/labels")["labels"]}


# ===================================================================== run ===
def main():
    hasta = SEMANA + timedelta(days=5)

    paso(1, "Capturar una idea desde una nota")
    antes = (VAULT / NOTA).read_text()
    nuevas = capturar.capturar(VAULT, NOTA)
    otra = capturar.capturar(VAULT, NOTA)
    ficha = nuevas[0] if nuevas else None
    check(1, "la idea de la nota diaria se volvió una ficha en Proyectos/", ficha and ficha.exists(),
          str(ficha.relative_to(VAULT)) if ficha else "")
    check(1, "la línea de la nota quedó enlazada a la ficha", "→ [[" in (VAULT / NOTA).read_text())
    check(1, "capturar dos veces no duplica", otra == [])
    check(1, "la línea que no es idea («Llamar a la imprenta») no se tocó",
          "- Llamar a la imprenta por las tarjetas\n" in (VAULT / NOTA).read_text())
    guardar("1-captura", {"nota_antes": antes, "nota_despues": (VAULT / NOTA).read_text(),
                          "ficha": ficha.read_text() if ficha else None})

    paso(2, "Convertirla en proyecto con próximas acciones")
    acc_file = capturar.a_proyecto(VAULT, ficha, [
        "Definir las 10 preguntas del diagnóstico [estimate:: 1h] [energy:: deep]",
        "Armar la planilla de puntaje [estimate:: 45m]",
        "Probarlo con un cliente amigo [estimate:: 30m]"],
        "lo probó un cliente amigo y quedó la planilla con puntajes")
    salida = {"init": ot("vault", "init", str(ACC), "--adopt"), "sync": ot("vault", "sync", str(ACC))}
    capturar.secuencial(acc_file)                      # 1.6.0 ignora la clave en un archivo nuevo
    salida["secuencial"] = ot("vault", "sync", str(ACC))
    segunda = {"Acciones": ot("vault", "sync", str(ACC))}
    proys = claude.mcp("list_projects")["projects"]
    ts = tareas()
    nombres = sorted(p["untrusted_text"]["name"] for p in proys)
    check(2, "cada ficha es un proyecto de OpenTodo (4)", len(proys) == 4, ", ".join(nombres))
    check(2, "cada línea de «Próximas acciones» es una tarea (11)", len(ts) == 11, f"{len(ts)} tareas")
    check(2, "la segunda sincronización no crea nada", all("up to date" in s for s in segunda.values()),
          json.dumps(segunda, ensure_ascii=False))
    txt, atxt = ficha.read_text(), acc_file.read_text()
    fm_ok = all(k in txt for k in ("tipo: entregable", "estado: en curso", "prioridad: siguiente", "quien: Persona", "proxima_accion:"))
    check(2, "la ficha queda en su lugar, intacta para director.py/hoy.py (OpenTodo no la toca)", fm_ok and "opentodo-id" not in txt)
    check(2, "Acciones/<ficha>.md enlaza la ficha y cada línea tiene su 🆔", 'ficha: "[[' in atxt and atxt.count("🆔") == 3)
    check(2, "las otras 3 fichas existentes también son proyectos (adoptadas sin tocarlas)",
          all("opentodo-id" not in f.read_text() for f in VAULT.glob("10-Empresas/*/Proyectos/*.md")))
    disp = [t["untrusted_text"]["title"] for t in claude.all_tasks(available=True)
            if t["untrusted_text"].get("project", "").startswith("Diagnóstico")]
    check(2, "proyecto secuencial: solo la primera acción queda disponible (GTD)", disp == ["Definir las 10 preguntas del diagnóstico"], str(disp))
    guardar("2-proyecto", {"ot_vault": salida, "segunda_sync": segunda, "ficha": txt, "acciones": atxt, "proyectos": nombres})

    paso(3, "Leer compromisos de calendario")
    principal, bloques = cal("principal", "Principal (copia de Google)"), cal("bloques", "Bloques OpenTodo")
    # Compromisos ficticios con la forma de una semana real (4 fijos). COMPROMISOS=<json> usa otra copia local.
    compromisos = json.loads(Path(os.environ.get("COMPROMISOS", "fixtures/compromisos.json")).read_text())
    for c0 in compromisos:
        uid, t, s, e, rr = c0["uid"], c0["titulo"], c0["inicio"], c0["fin"], c0["rrule"]
        evento(principal, uid, t, s, e, rr)
        evento(principal, uid, t, s, e, rr)            # dos veces: el UID evita el duplicado
    conn = persona.rest("POST", "/api/v1/calendar-sync/connections", {
        "name": "Google (sandbox CalDAV)", "server_url": "http://127.0.0.1:5232/persona/",
        "username": "persona", "password": "sandbox-pass"})["connection"]
    CONN["id"] = conn["id"]
    persona.rest("PATCH", f"/api/v1/calendar-sync/connections/{conn['id']}",
                 {"target": "http://127.0.0.1:5232/persona/bloques/", "read": ["http://127.0.0.1:5232/persona/principal/"]})
    c = sync_cal(lambda: len(eventos_ot(SEMANA, hasta)) >= 4)
    evs = eventos_ot(SEMANA, hasta)
    check(3, "OpenTodo lee los 4 compromisos de la semana", len(evs) == 4,
          ", ".join(f"{e['summary']} {e['start']['date'][5:]} {e['start']['time']}" for e in evs))
    libre = claude.mcp("find_free_time", {"from": str(SEMANA), "to": str(SEMANA + timedelta(days=4)), "min_minutes": 30,
                                          "day_start_hour": 9, "day_end_hour": 19, "timezone": "America/Argentina/Buenos_Aires"})
    martes = next(d for d in libre["days"] if d["date"] == "2026-11-24")
    check(3, "find_free_time deja afuera los dos compromisos del martes",
          [(f["start"], f["end"]) for f in martes["free"]] == [("09:00", "10:00"), ("11:00", "13:30"), ("14:30", "19:00")],
          str([(f["start"], f["end"]) for f in martes["free"]]))
    guardar("3-calendario", {"conexion": c, "eventos": evs, "libre": libre})

    paso(4, "Proponer bloques horarios automáticamente")
    claude.mcp("create_label", {"name": "propuesta", "color": "#f59e0b", "client_request_id": "lbl-prop"})
    claude.mcp("create_label", {"name": "rechazada", "color": "#ef4444", "client_request_id": "lbl-rech"})
    l1 = plan("proponer", "--desde", str(SEMANA), "--dias", "5")
    l1b = plan("proponer", "--desde", str(SEMANA), "--dias", "5")
    props = propuestas()
    titulos = {t["untrusted_text"]["title"] for t in props}
    check(4, "propuso bloques para las acciones con estimación", len(l1["cambios"]) == len(props) and len(props) >= 6,
          f"{len(props)} bloques en {l1['solve_ms']} ms (Horolog)")
    check(4, "ningún bloque pisa un compromiso", not any(solapa(t, evs) for t in props))
    check(4, "respeta energía: [energy:: deep] solo a la mañana",
          all(planificar.due_dt(t["due"]).hour < 13 for t in props if t.get("energy") == "deep"))
    check(4, "no agenda la ficha bloqueada (Web de Ancla)", "Maquetar la portada" not in titulos)
    check(4, "no agenda acciones que todavía no son la siguiente (proyecto secuencial)",
          "Armar la planilla de puntaje" not in titulos and "Definir las 10 preguntas del diagnóstico" in titulos)
    est = plan("estado", "--desde", str(SEMANA), "--dias", "5")
    check(4, "avisa lo que no puede agendar (sin estimación)", any(f["estado"] == "sin estimación" for f in est))
    check(4, "correr dos veces no cambia nada (idempotente)", l1b.get("sin_cambios") is True)
    sync_cal(lambda: len(eventos_caldav(bloques)) == len(con_hora(tareas())))
    evb = eventos_caldav(bloques)
    check(4, "cada bloque está una sola vez en el calendario «Bloques»",
          len(evb) == len(props) and len({e["uid"] for e in evb}) == len(evb), f"{len(evb)} eventos")
    check(4, "el calendario principal no se tocó", len(eventos_caldav(principal)) == 4)
    guardar("4-propuesta", {"lote": l1, "estado": est, "eventos_bloques": evb})

    paso(5, "Mostrar el día y la semana")
    primero = min(props, key=lambda t: planificar.due_dt(t["due"]))
    foto("5-semana-propuesta", f"/week/{SEMANA}")
    foto("5-dia-propuesta", f"/day/{planificar.due_dt(primero['due']).date()}")
    check(5, "capturas de Semana y Día", (WORK / "capturas" / "5-semana-propuesta.png").exists())

    paso(6, "Replanificar ante una reunión imprevista")
    victima = min((t for t in props if planificar.due_dt(t["due"]).date() > SEMANA),
                  key=lambda t: planificar.due_dt(t["due"]))
    s = planificar.due_dt(victima["due"]) - timedelta(minutes=30)
    f = s + timedelta(hours=2)
    evento(principal, "imprevista", "Reunión imprevista con cliente [ficticio]", s.strftime("%Y%m%dT%H%M00"), f.strftime("%Y%m%dT%H%M00"))
    sync_cal(lambda: len(eventos_ot(SEMANA, hasta)) == 5)
    evs = eventos_ot(SEMANA, hasta)
    choques = [t["untrusted_text"]["title"] for t in propuestas() if solapa(t, evs)]
    l2 = plan("replanificar", "--desde", str(SEMANA), "--dias", "5")
    movidas = [c["titulo"] for c in l2["cambios"]]
    check(6, "detecta el choque con la reunión nueva", len(choques) >= 1, ", ".join(choques))
    check(6, "mueve solo lo que choca (o lo mínimo)", set(choques) <= set(movidas) and len(movidas) <= len(choques) + 1,
          f"movidas: {', '.join(movidas)}")
    check(6, "después de replanificar nada pisa un compromiso", not any(solapa(t, evs) for t in propuestas()))
    if l2.get("sin_cambios"):
        raise SystemExit("replanificar no cambió nada: no hay lote para revertir")
    rv = planificar.revertir(claude, planificar.Lotes(Path(os.environ["LOTES"])), l2["id"])
    vuelta = [t for t in propuestas() if t["id"] == victima["id"]][0]
    check(6, "revertir el lote devuelve el bloque a su lugar anterior",
          planificar.mismo_due(vuelta["due"], victima["due"]), json.dumps(rv, ensure_ascii=False))
    l2b = plan("replanificar", "--desde", str(SEMANA), "--dias", "5")
    check(6, "replanificar otra vez da el mismo resultado (determinista)",
          sorted(c["titulo"] for c in l2b["cambios"]) == sorted(movidas))
    sync_cal(lambda: len(eventos_caldav(bloques)) == len(con_hora(tareas())))
    evb = eventos_caldav(bloques)
    check(6, "el evento del bloque se movió, no se duplicó", len(evb) == len(con_hora(tareas())) and len({e["uid"] for e in evb}) == len(evb))
    foto("6-semana-replanificada", f"/week/{SEMANA}")
    guardar("6-replan", {"reunion": [str(s), str(f)], "choques": choques, "lote": l2, "revertido": rv, "lote_otra_vez": l2b})

    paso("6b", "Replanificación nativa de OpenTodo (bloques atrasados de hoy)")
    hoy = datetime.now(TZ)
    t0 = (hoy - timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
    nuevas = claude.mcp("create_tasks", {"items": [
        {"title": "Contestar mails de la mañana [ficticio]", "estimate_minutes": 45,
         "due": {"date": t0.strftime("%Y-%m-%d"), "time": t0.strftime("%H:%M"), "tz": "America/Argentina/Buenos_Aires"}},
        {"title": "Revisar el borrador del contador [ficticio]", "estimate_minutes": 30,
         "due": {"date": t0.strftime("%Y-%m-%d"), "time": (t0 + timedelta(hours=1)).strftime("%H:%M"), "tz": "America/Argentina/Buenos_Aires"}}],
        "client_request_id": "demo-6b"})
    ids6 = [r["id"] for r in nuevas["results"]] if "results" in nuevas else nuevas.get("ids", [])
    im0 = (hoy + timedelta(minutes=45)).replace(second=0, microsecond=0)
    im0 = im0.replace(minute=(im0.minute // 15) * 15)
    evento(principal, "imprevista-hoy", "Llamada imprevista [ficticio]", im0.strftime("%Y%m%dT%H%M00"), (im0 + timedelta(hours=1)).strftime("%Y%m%dT%H%M00"))
    sync_cal(lambda: any(e["uid"].startswith("imprevista-hoy") for e in eventos_ot(hoy.date(), hoy.date() + timedelta(days=1))))
    ok = foto("6b-dia-hoy", "/day", "replan")
    ev_hoy = eventos_ot(hoy.date(), hoy.date() + timedelta(days=1))
    movidas_hoy = [claude.mcp("get_task", {"id": i})["task"] for i in ids6]
    check("6b", "«Replanificar» de OpenTodo movió los bloques atrasados después de ahora, sin pisar la llamada",
          ok and all(planificar.due_dt(t["due"]) >= hoy - timedelta(minutes=15) and not solapa(t, ev_hoy) for t in movidas_hoy),
          ", ".join(f"{t['untrusted_text']['title'][:25]} → {planificar.due_dt(t['due']):%H:%M}" for t in movidas_hoy))
    guardar("6b-replan-nativo", {"tareas": movidas_hoy, "eventos_hoy": ev_hoy})

    paso(7, "Aceptar, editar o rechazar propuestas (como la persona)")
    props = sorted(propuestas(), key=lambda t: planificar.due_dt(t["due"]))
    A, Bt, D = props[0], props[1], props[-1]
    C = next(t for t in props if t["id"] not in {A["id"], Bt["id"], D["id"]})
    ids = label_ids()
    # aceptar: sacarle la etiqueta (en la app: Etiquetas, o selección múltiple → Etiquetas)
    persona.rest("PATCH", f"/api/v1/tasks/{A['id']}", {"labels": [ids[n] for n in planificar.etiquetas(A) if n != "propuesta"]})
    # editar en la app: lo mismo que arrastrar el bloque al jueves 16:00
    persona.rest("PATCH", f"/api/v1/tasks/{Bt['id']}", {"due": {"date": "2026-11-26", "time": "16:00", "tz": "America/Argentina/Buenos_Aires"}})
    # editar en Obsidian: cambiar [time:: ] en la línea de la ficha y sincronizar
    for c in CARPETAS:
        ot("vault", "sync", str(c))
    hora_c = planificar.due_dt(C["due"])
    nueva_c = (hora_c + timedelta(hours=1)).strftime("%H:%M")
    for fpath in ACC.glob("*.md"):
        lineas = fpath.read_text().splitlines()
        for i, l in enumerate(lineas):
            if C["untrusted_text"]["title"] in l and "[time:: " in l:
                import re
                lineas[i] = re.sub(r"\[time:: \d\d:\d\d\]", f"[time:: {nueva_c}]", l)
                fpath.write_text("\n".join(lineas) + "\n")
                editada_en = fpath
    sync_obs = ot("vault", "sync", str(ACC))
    # rechazar: ponerle la etiqueta «rechazada»
    persona.rest("PATCH", f"/api/v1/tasks/{D['id']}", {"labels": [ids[n] for n in planificar.etiquetas(D)] + [ids["rechazada"]]})
    l3 = plan("proponer", "--desde", str(SEMANA), "--dias", "5")
    est = plan("estado", "--desde", str(SEMANA), "--dias", "5")
    get = lambda t: claude.mcp("get_task", {"id": t["id"], "timezone": "America/Argentina/Buenos_Aires"})["task"]
    a2, b2, c2, d2 = get(A), get(Bt), get(C), get(D)
    check(7, "aceptada: queda fija en su horario, sin etiqueta", planificar.mismo_due(a2["due"], A["due"]) and "propuesta" not in planificar.etiquetas(a2))
    check(7, "editada en la app: se respeta tu horario (jue 16:00) y cuenta como aceptada",
          planificar.due_dt(b2["due"]) == datetime(2026, 11, 26, 16, 0, tzinfo=TZ) and "propuesta" not in planificar.etiquetas(b2))
    check(7, "editada en Obsidian: el cambio de [time:: ] llegó a OpenTodo y se respeta",
          planificar.due_dt(c2["due"]).strftime("%H:%M") == nueva_c and "propuesta" not in planificar.etiquetas(c2),
          f"{hora_c:%a %H:%M} → {nueva_c}")
    check(7, "rechazada: sale del calendario y no se vuelve a proponer",
          planificar.due_dt(d2["due"]) is None and "propuesta" not in planificar.etiquetas(d2))
    l3b = plan("proponer", "--desde", str(SEMANA), "--dias", "5")
    check(7, "la corrida siguiente no la vuelve a proponer", l3b.get("sin_cambios") is True or all(c["task_id"] != D["id"] for c in l3b["cambios"]))
    evs = eventos_ot(SEMANA, hasta)
    check(7, "nada pisa un compromiso después de la revisión", not any(solapa(t, evs) for t in con_hora(tareas()) if planificar.due_dt(t["due"]).date() >= SEMANA))
    foto("7-semana-revisada", f"/week/{SEMANA}")
    check(7, "filtro nativo del calendario: solo lo que falta revisar (@propuesta)",
          foto("7-semana-solo-propuestas", f"/week/{SEMANA}", "filtro:@propuesta"))
    guardar("7-revision", {"aceptada": A["untrusted_text"]["title"], "editada_app": Bt["untrusted_text"]["title"],
                           "editada_obsidian": C["untrusted_text"]["title"], "rechazada": D["untrusted_text"]["title"],
                           "sync_obsidian": sync_obs, "lote": l3, "estado": est})

    paso(8, "Sincronizar sin duplicados y revertir")
    for c in CARPETAS:
        ot("vault", "sync", str(c))
    sync_cal(lambda: len(eventos_caldav(bloques)) == len(con_hora(tareas())))
    evb, th = eventos_caldav(bloques), con_hora(tareas())
    check(8, "calendario «Bloques» = tareas con hora, sin UID repetido", len(evb) == len(th) and len({e["uid"] for e in evb}) == len(evb),
          f"{len(evb)} eventos / {len(th)} tareas")
    check(8, "OpenTodo nunca escribió en el calendario principal", {e["uid"].split("@")[0] for e in eventos_caldav(principal)} ==
          {c0["uid"] for c0 in compromisos} | {"imprevista", "imprevista-hoy"})
    lineas_con_hora = sum(l.count("[time:: ") for fp in ACC.glob("*.md") if fp.name != "Inbox.md"
                          for l in fp.read_text().splitlines())
    check(8, "las fichas tienen el horario de cada bloque (una línea por tarea, sin copias)",
          lineas_con_hora == len([t for t in th if t.get("project_id")]), f"{lineas_con_hora} líneas con [time:: ]")
    hist = persona.rest("GET", f"/api/v1/tasks/{A['id']}/history")
    guardar("8-historial-tarea-aceptada", hist)
    diff = subprocess.run(["git", "-C", str(VAULT), "diff", "--stat"], capture_output=True, text=True).stdout
    lotes = planificar.Lotes(Path(os.environ["LOTES"]))
    reversa = [planificar.revertir(claude, lotes, l["id"]) for l in reversed(lotes.todos()) if not l.get("revertido")]
    for c in CARPETAS:
        ot("vault", "sync", str(c))
    sync_cal(lambda: len(eventos_caldav(bloques)) == len(con_hora(tareas())))
    quedan = {t["untrusted_text"]["title"] for t in con_hora(tareas()) if planificar.due_dt(t["due"]).date() >= SEMANA}
    tocadas = {A["untrusted_text"]["title"], Bt["untrusted_text"]["title"], C["untrusted_text"]["title"]}
    saltadas = {x for r in reversa for x in r.get("saltados_porque_cambiaron_despues", [])}
    check(8, "revertir todo deshace lo del planificador y respeta lo que tocaste vos", quedan == tocadas,
          f"quedan: {sorted(quedan)}; saltadas: {sorted(saltadas)}")
    check(8, "después de revertir, el calendario «Bloques» sigue igual a las tareas con hora",
          len(eventos_caldav(bloques)) == len(con_hora(tareas())))
    diff2 = subprocess.run(["git", "-C", str(VAULT), "diff", "--stat"], capture_output=True, text=True).stdout
    foto("8-semana-revertida", f"/week/{SEMANA}")
    guardar("8-sync-y-reversa", {"eventos_bloques": evb, "git_diff_antes": diff, "reversa": reversa, "git_diff_despues": diff2})

    (EV / "chequeos.json").write_text(json.dumps(CHEQUEOS, ensure_ascii=False, indent=2))
    fallas = [c for c in CHEQUEOS if not c["ok"]]
    print(f"\n{len(CHEQUEOS) - len(fallas)}/{len(CHEQUEOS)} chequeos OK")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
