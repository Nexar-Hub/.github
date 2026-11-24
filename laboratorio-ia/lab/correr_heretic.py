#!/usr/bin/env python3
"""
Corre Heretic con opciones pensadas para el laboratorio:

- pregunta qué modelo modificar (y lo recuerda en modelos/modelo-base.txt),
- mira cuánta memoria tiene tu placa y, si el modelo no entra, activa 4 bits,
- guarda el resultado en modelos/modificado, que es donde lo busca el laboratorio.

Cualquier opción extra se le pasa a Heretic tal cual, por ejemplo:
    python lab/correr_heretic.py --n-trials 200
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "modelos"
ARCHIVO_MODELO_BASE = MODELOS / "modelo-base.txt"
CARPETA_SALIDA = MODELOS / "modificado"
POR_DEFECTO = "Qwen/Qwen3-4B-Instruct-2507"

GB = 1024**3


def peso_del_modelo(modelo: str) -> int | None:
    """Tamaño de los pesos en bytes (en bf16), o None si no se puede saber."""
    ruta = Path(modelo).expanduser()
    if ruta.is_dir():
        return sum(f.stat().st_size for f in ruta.glob("*.safetensors")) or None
    try:
        from huggingface_hub import HfApi

        info = HfApi().model_info(modelo, files_metadata=True)
        total = sum((s.size or 0) for s in info.siblings or [] if s.rfilename.endswith(".safetensors"))
        return total or None
    except Exception as e:  # noqa: BLE001
        print(f"  (no pude consultar el tamaño en Hugging Face: {type(e).__name__})")
        return None


def vram_total() -> int | None:
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory
    except Exception:  # noqa: BLE001
        pass
    return None


def main() -> None:
    MODELOS.mkdir(exist_ok=True)
    anterior = POR_DEFECTO
    if ARCHIVO_MODELO_BASE.is_file():
        anterior = ARCHIVO_MODELO_BASE.read_text(encoding="utf-8").strip() or POR_DEFECTO

    print()
    print("=== Heretic: modificar un modelo ===")
    print()
    print("Escribí el ID de Hugging Face del modelo (o la ruta a una carpeta).")
    print("Tiene que ser una versión «Instruct» o de chat.")
    try:
        respuesta = input(f"Modelo [Enter = {anterior}]: ").strip()
    except EOFError:
        respuesta = ""
    modelo = respuesta or anterior
    ARCHIVO_MODELO_BASE.write_text(modelo + "\n", encoding="utf-8")

    extra: list[str] = []
    vram = vram_total()
    peso = peso_del_modelo(modelo)
    print()
    if vram is None:
        print("[!] PyTorch no ve ninguna GPU NVIDIA. Heretic va a ser MUY lento en CPU.")
        print("    Revisá que hayas corrido el instalador y que el driver de NVIDIA esté al día.")
    else:
        print(f"GPU: {vram / GB:.1f} GB de VRAM")
    if peso:
        print(f"Modelo: {peso / GB:.1f} GB de pesos")

    if "--quantization" not in sys.argv and vram and peso and peso * 1.25 + 2 * GB > vram:
        extra += ["--quantization", "bnb_4bit"]
        print()
        print("-> No entra completo en tu placa: lo cargo en 4 bits (pierde un poquito de precisión).")
        print(f"   Ojo: al guardar, Heretic rearma el modelo completo en la RAM. Necesitás unos {peso * 1.5 / GB:.0f} GB de RAM libres.")

    if CARPETA_SALIDA.exists() and any(CARPETA_SALIDA.iterdir()):
        print()
        print(f"[!] Ya hay un modelo en {CARPETA_SALIDA}. Si guardás uno nuevo, lo pisa.")

    print()
    print("Qué va a pasar:")
    print("  1. Descarga el modelo (solo la primera vez) y prueba cuánta memoria usar.")
    print("  2. Hace ~100 pruebas («trials»). Un modelo de 4B tarda ~30-45 min en una placa buena.")
    print("  3. Al final te muestra una lista así:")
    print("       [Trial  42] Refusals: 3/100, KL divergence: 0.0912")
    print("     Refusals = cuántas de 100 preguntas sigue rechazando (menos es mejor).")
    print("     KL divergence = cuánto cambió su «cerebro» (menos es mejor; arriba de ~1 se nota).")
    print("     Elegí uno con pocos rechazos Y KL bajo, no solo el de menos rechazos.")
    print("  4. Elegí «Save the model to a local folder». Se guarda solo en modelos/modificado.")
    print("     Podés probar antes con «Chat with the model». Para salir: «Exit program».")
    print()

    heretic = shutil.which("heretic")
    if heretic is None:
        print("[!] No encuentro Heretic. Corré primero el instalador.")
        sys.exit(1)

    comando = [
        heretic,
        "--model", modelo,
        "--export-strategy", "merge",
        "--save-directory", str(CARPETA_SALIDA),
        *extra,
        *sys.argv[1:],
    ]
    print("Comando:", " ".join(comando))
    print()
    try:
        codigo = subprocess.call(comando, cwd=RAIZ)
    except KeyboardInterrupt:
        codigo = 130
    print()
    if CARPETA_SALIDA.exists() and any(CARPETA_SALIDA.glob("*.safetensors")):
        print("Listo. Ahora abrí el laboratorio para comparar el original con el modificado.")
    else:
        print("No veo un modelo guardado en modelos/modificado todavía.")
        print("Si cortaste a la mitad, al volver a correrlo Heretic te ofrece seguir desde donde quedó.")
    sys.exit(codigo)


if __name__ == "__main__":
    main()
