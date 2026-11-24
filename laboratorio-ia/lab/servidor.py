#!/usr/bin/env python3
"""
Laboratorio de IA local.

Carga dos modelos (el original y el modificado por Heretic) con transformers
y sirve una página web para compararlos lado a lado y para armar una
"mesa de consejeros".

Uso:
    python lab/servidor.py --original Qwen/Qwen3-4B-Instruct-2507 --modificado modelos/modificado

Todo corre en tu computadora. No se manda nada a internet (salvo la primera
descarga del modelo original desde Hugging Face, si no lo tenías).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
ARCHIVO_MODELO_BASE = RAIZ / "modelos" / "modelo-base.txt"
MODELO_POR_DEFECTO = "Qwen/Qwen3-4B-Instruct-2507"

# Una sola generación a la vez: la GPU es una sola.
CANDADO_GPU = threading.Lock()


def log(msg: str) -> None:
    print(f"[laboratorio] {msg}", flush=True)


def gb(n_bytes: float) -> str:
    return f"{n_bytes / 1024**3:.1f} GB"


class Modelo:
    def __init__(self, clave: str, origen: str | None):
        self.clave = clave
        self.origen = origen
        self.estado = "pendiente"  # pendiente | cargando | listo | falta | error
        self.detalle = ""
        self.cuantizado = False
        self.tokenizer = None
        self.model = None

    def info(self) -> dict:
        return {
            "nombre": self.origen or "",
            "estado": self.estado,
            "detalle": self.detalle,
            "cuantizado": self.cuantizado,
        }

    # ------------------------------------------------------------------ carga

    def _ruta_local(self) -> Path:
        """Devuelve la carpeta local del modelo (descargándolo si hace falta)."""
        ruta = Path(self.origen).expanduser()
        if ruta.is_dir():
            return ruta
        if ruta.exists() or self.origen.startswith((".", "/", "\\")) or ":" in self.origen[:3]:
            raise FileNotFoundError(f"No encuentro la carpeta {ruta}")
        from huggingface_hub import snapshot_download

        self.detalle = "descargando de Hugging Face (solo la primera vez)…"
        return Path(snapshot_download(self.origen))

    def cargar(self, modo_cuantizar: str) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if not self.origen:
            self.estado = "falta"
            self.detalle = "No se indicó ningún modelo."
            return

        ruta = Path(self.origen).expanduser()
        if self.clave == "modificado" and not ruta.is_dir():
            self.estado = "falta"
            self.detalle = (
                f"Todavía no existe la carpeta {ruta}. Corré Heretic y guardá el modelo ahí."
            )
            return

        self.estado = "cargando"
        try:
            carpeta = self._ruta_local()
            self.detalle = "cargando en memoria…"
            peso = sum(f.stat().st_size for f in carpeta.glob("*.safetensors"))

            hay_gpu = torch.cuda.is_available()
            usar_4bit = False
            if hay_gpu and modo_cuantizar == "4bit":
                usar_4bit = True
            elif hay_gpu and modo_cuantizar == "auto" and peso:
                libre, _total = torch.cuda.mem_get_info()
                # Pesos + ~15 % de margen + 1.5 GB para la generación.
                usar_4bit = peso * 1.15 + 1.5 * 1024**3 > libre
                log(
                    f"{self.clave}: pesa {gb(peso)}, VRAM libre {gb(libre)} -> "
                    + ("cargo en 4 bits" if usar_4bit else "cargo en precisión completa")
                )

            kwargs: dict = {"device_map": "auto" if hay_gpu else "cpu"}
            if usar_4bit:
                from transformers import BitsAndBytesConfig

                kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                )
            else:
                kwargs["dtype"] = "auto"

            self.tokenizer = AutoTokenizer.from_pretrained(carpeta)
            try:
                self.model = AutoModelForCausalLM.from_pretrained(carpeta, **kwargs)
            except (ValueError, KeyError):
                # Modelos multimodales (p. ej. Gemma 3) usan otra clase.
                from transformers import AutoModelForImageTextToText

                self.model = AutoModelForImageTextToText.from_pretrained(carpeta, **kwargs)
            self.model.eval()
            self.cuantizado = usar_4bit
            self.estado = "listo"
            self.detalle = ("GPU" if hay_gpu else "CPU (lento)") + (" · 4 bits" if usar_4bit else "")
            log(f"{self.clave}: listo ({self.detalle})")
        except Exception as e:  # noqa: BLE001
            self.estado = "error"
            self.detalle = f"{type(e).__name__}: {e}"
            log(f"{self.clave}: error al cargar\n{traceback.format_exc()}")

    # ------------------------------------------------------------- generación

    def _prompt(self, mensajes: list[dict]) -> str:
        tok = self.tokenizer
        try:
            # enable_thinking=False apaga el "modo pensar" en los modelos que lo tienen;
            # las plantillas que no lo usan lo ignoran.
            return tok.apply_chat_template(
                mensajes, tokenize=False, add_generation_prompt=True, enable_thinking=False
            )
        except Exception:
            # Algunas plantillas no aceptan el rol "system": lo pegamos al primer mensaje.
            if mensajes and mensajes[0]["role"] == "system":
                sistema, resto = mensajes[0]["content"], [dict(m) for m in mensajes[1:]]
                if resto and resto[0]["role"] == "user":
                    resto[0]["content"] = f"{sistema}\n\n{resto[0]['content']}"
                return tok.apply_chat_template(resto, tokenize=False, add_generation_prompt=True)
            raise

    def generar(self, mensajes, max_tokens, temperatura, cancelado: threading.Event):
        """Generador que va devolviendo pedazos de texto."""
        import torch
        from transformers import StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer

        class Cortar(StoppingCriteria):
            def __call__(self, input_ids, scores, **kwargs):
                return cancelado.is_set()

        tok = self.tokenizer
        texto = self._prompt(mensajes)
        entradas = tok(texto, return_tensors="pt", add_special_tokens=False).to(self.model.device)
        streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True, timeout=600)
        params = dict(
            **entradas,
            max_new_tokens=max_tokens,
            streamer=streamer,
            stopping_criteria=StoppingCriteriaList([Cortar()]),
            pad_token_id=tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id,
        )
        if temperatura > 0:
            params.update(do_sample=True, temperature=temperatura, top_p=0.95)
        else:
            params.update(do_sample=False)

        error: list[BaseException] = []

        def correr():
            try:
                with torch.inference_mode():
                    self.model.generate(**params)
            except BaseException as e:  # noqa: BLE001
                error.append(e)
                streamer.end()

        hilo = threading.Thread(target=correr, daemon=True)
        hilo.start()
        for pedazo in streamer:
            if pedazo:
                yield pedazo
        hilo.join()
        if error:
            raise error[0]


MODELOS: dict[str, Modelo] = {}
INFO_GPU: dict = {}


def cargar_todo(modo_cuantizar: str) -> None:
    try:
        import torch

        if torch.cuda.is_available():
            _libre, total = torch.cuda.mem_get_info()
            INFO_GPU.update(nombre=torch.cuda.get_device_name(0), vram=gb(total))
        else:
            INFO_GPU.update(nombre="sin GPU (CPU)", vram="")
            log("No detecto GPU NVIDIA: va a funcionar, pero muy lento.")
    except Exception as e:  # noqa: BLE001
        INFO_GPU.update(nombre=f"error: {e}", vram="")
    for m in MODELOS.values():
        m.cargar(modo_cuantizar)


class Manejador(BaseHTTPRequestHandler):
    server_version = "Laboratorio/1.0"

    def log_message(self, fmt, *args):  # silencio los logs de cada pedido
        pass

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            cuerpo = (AQUI / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)
        elif self.path == "/api/estado":
            self._json({"gpu": INFO_GPU, "modelos": {k: m.info() for k, m in MODELOS.items()}})
        else:
            self._json({"error": "no existe"}, 404)

    def do_POST(self):
        if self.path != "/api/chat":
            return self._json({"error": "no existe"}, 404)
        try:
            largo = int(self.headers.get("Content-Length", 0))
            pedido = json.loads(self.rfile.read(largo) or b"{}")
            modelo = MODELOS.get(pedido.get("modelo", ""))
            mensajes = pedido["mensajes"]
            max_tokens = max(1, min(int(pedido.get("max_tokens", 400)), 4096))
            temperatura = max(0.0, min(float(pedido.get("temperatura", 0.7)), 2.0))
        except Exception as e:  # noqa: BLE001
            return self._json({"error": f"pedido inválido: {e}"}, 400)
        if modelo is None or modelo.estado != "listo":
            estado = modelo.estado if modelo else "desconocido"
            return self._json({"error": f"el modelo no está listo ({estado})"}, 409)

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        cancelado = threading.Event()

        def enviar(obj) -> None:
            try:
                self.wfile.write((json.dumps(obj, ensure_ascii=False) + "\n").encode())
                self.wfile.flush()
            except OSError:
                # El navegador cortó (botón "Detener" o cerró la pestaña).
                cancelado.set()

        enviar({"esperando": True})
        with CANDADO_GPU:
            enviar({"empezo": True})
            if cancelado.is_set():
                return
            inicio, n = time.time(), 0
            try:
                for pedazo in modelo.generar(mensajes, max_tokens, temperatura, cancelado):
                    n += 1
                    enviar({"t": pedazo})
                    if cancelado.is_set():
                        break
                enviar({"fin": True, "segundos": round(time.time() - inicio, 1), "pedazos": n})
            except Exception as e:  # noqa: BLE001
                log(f"error generando: {traceback.format_exc()}")
                enviar({"error": f"{type(e).__name__}: {e}"})


def main() -> None:
    modelo_base = MODELO_POR_DEFECTO
    if ARCHIVO_MODELO_BASE.is_file():
        modelo_base = ARCHIVO_MODELO_BASE.read_text(encoding="utf-8").strip() or modelo_base

    p = argparse.ArgumentParser(description="Laboratorio: antes/después y mesa de consejeros.")
    p.add_argument("--original", default=modelo_base, help="ID de Hugging Face o carpeta del modelo original")
    p.add_argument("--modificado", default=str(RAIZ / "modelos" / "modificado"), help="carpeta donde Heretic guardó el modelo")
    p.add_argument("--puerto", type=int, default=8765)
    p.add_argument("--cuantizar", choices=["auto", "4bit", "no"], default="auto",
                   help="auto: usa 4 bits solo si no entra en la VRAM")
    p.add_argument("--no-abrir", action="store_true", help="no abrir el navegador")
    args = p.parse_args()

    MODELOS["original"] = Modelo("original", args.original)
    MODELOS["modificado"] = Modelo("modificado", args.modificado)

    threading.Thread(target=cargar_todo, args=(args.cuantizar,), daemon=True).start()

    servidor = ThreadingHTTPServer(("127.0.0.1", args.puerto), Manejador)
    url = f"http://localhost:{args.puerto}"
    log(f"Abrí {url} en el navegador (Ctrl+C para cerrar).")
    if not args.no_abrir:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        log("Chau.")
        sys.exit(0)


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
