# Laboratorio de IA local

Tu propio laboratorio, corriendo 100 % en tu PC:

- **Antes / Después**: le mandás el mismo mensaje al modelo original y al modificado con [Heretic](https://github.com/p-e-w/heretic), y ves lado a lado cuál rechaza, cuál sermonea y cuál responde.
- **Mesa de consejeros**: llevás una decisión real y la discuten cuatro personajes (La Honesta, El Abogado del Diablo, La Visionaria y El Práctico). Se responden entre ellos y al final un moderador da un veredicto con próximos pasos. Los personajes se pueden editar.

Nada sale de tu compu. Internet se usa solo la primera vez, para instalar y bajar el modelo.

## Qué necesitás

- PC con placa **NVIDIA** (8 GB de VRAM o más) y el driver actualizado.
- **Python 3.12** de [python.org](https://www.python.org/downloads/). Al instalarlo, marcá **"Add python.exe to PATH"**.
- Unos **25 GB libres** en disco y **16 GB de RAM**.

## Cómo bajarlo

En GitHub, entrá a la rama `claude/heretic-uncensoring-setup-he1ca5`, tocá **Code → Download ZIP** y descomprimilo. Después abrí la carpeta `laboratorio-ia`.

O con git:

```
git clone -b claude/heretic-uncensoring-setup-he1ca5 https://github.com/nexar-hub/.github.git
cd .github/laboratorio-ia
```

## Paso a paso (Windows)

Hacé doble clic en cada archivo, en orden:

| Paso | Archivo | Qué hace | Tiempo |
|---|---|---|---|
| 1 | `1-instalar.bat` | Instala PyTorch con soporte para tu placa y Heretic, en una carpeta `.venv` que no toca nada más de tu PC. | 10–20 min |
| 2 | `2-correr-heretic.bat` | Modifica el modelo y lo guarda en `modelos/modificado`. | 30–60 min |
| 3 | `3-abrir-laboratorio.bat` | Carga los dos modelos y abre el laboratorio en el navegador. | 1–3 min |

En Linux es lo mismo con `./instalar.sh`, `./correr-heretic.sh` y `./abrir-laboratorio.sh`.

### El paso 2 en detalle

1. Te pregunta qué modelo querés modificar. Con **Enter** usa `Qwen/Qwen3-4B-Instruct-2507`, que es chico, bueno en español y rápido de procesar.
2. Si el modelo no entra en tu placa, el script activa solo el modo de 4 bits.
3. Heretic hace unas 100 pruebas. Al final te muestra una lista como esta:

   ```
   [Trial  42] Refusals: 3/100, KL divergence: 0.0912
   [Trial  17] Refusals: 1/100, KL divergence: 0.4310
   ```

   - **Refusals**: cuántas de 100 preguntas sigue rechazando. Menos es mejor.
   - **KL divergence**: cuánto cambió el "cerebro" del modelo. Menos es mejor. Por debajo de ~0,2 casi no se nota; por encima de ~1 empieza a perder calidad.
   - **Elegí uno con pocos rechazos *y* KL bajo.** En el ejemplo, el trial 42 suele ser mejor que el 17.
4. Elegí **"Save the model to a local folder"**. Se guarda solo en `modelos/modificado`, que es donde lo busca el laboratorio. Antes de guardar podés probarlo con **"Chat with the model"**.

Si se corta a la mitad, volvé a correrlo: Heretic te ofrece seguir desde donde quedó.

## Qué modelo elegir según tu placa

| VRAM | Modelo recomendado |
|---|---|
| 8–10 GB | `Qwen/Qwen3-4B-Instruct-2507` (se carga en 4 bits automáticamente) |
| 12–16 GB | `Qwen/Qwen3-4B-Instruct-2507` en precisión completa, o `Qwen/Qwen3-8B` |
| 24 GB | `google/gemma-3-12b-it` (*) |

(*) Los modelos de Google y Meta piden aceptar la licencia en su página de Hugging Face. Después tenés que iniciar sesión una vez: abrí una terminal en esta carpeta y corré `.venv\Scripts\hf auth login`.

## Cómo usar el laboratorio

**Antes / Después**
- Tocá un ejemplo o escribí lo que quieras. El mismo mensaje va a los dos modelos, que responden de a uno porque la GPU es una sola.
- Arriba se lleva la cuenta de cuántas veces cada modelo rechazó o sermoneó. Se detecta por palabras clave, así que es orientativo.
- En **Ajustes** podés cambiar la temperatura, el largo de las respuestas y una instrucción de sistema común a los dos.

**Mesa de consejeros**
- Contá tu situación con detalle y tocá **Convocar a la mesa**.
- **Otra ronda** hace que se discutan entre ellos. **Veredicto** pide la síntesis final. Abajo podés agregar datos o repreguntar.
- Tocá un integrante para sacarlo de la mesa, o usá **Editar integrantes** para cambiarles la personalidad o crear nuevos (por ejemplo, "Mi viejo", "Un inversor" o "Yo dentro de 10 años").
- **Copiar acta** copia toda la discusión en texto.

## Si algo falla

| Problema | Solución |
|---|---|
| "PyTorch no ve la GPU" | Actualizá el driver de NVIDIA. Si tu placa es GTX 10xx o más vieja, cambiá `cu128` por `cu126` en `1-instalar.bat`, borrá `.venv` y volvé a instalar. |
| Error de memoria (*out of memory*) en Heretic | Abrí una terminal en esta carpeta y corré `2-correr-heretic.bat --quantization bnb_4bit`. |
| Error de memoria en el laboratorio | `3-abrir-laboratorio.bat --cuantizar 4bit` |
| El puerto 8765 está ocupado | `3-abrir-laboratorio.bat --puerto 8888` |
| Quiero comparar otro modelo ya guardado | `3-abrir-laboratorio.bat --original <ID o carpeta> --modificado <carpeta>` |
| Quiero más pruebas para un mejor resultado | `2-correr-heretic.bat --n-trials 200` |

Los modelos descargados quedan en `C:\Users\<tu usuario>\.cache\huggingface` y ocupan varios GB. Si un día querés liberar espacio, se pueden borrar desde ahí.

## Extra (opcional): usar el modelo en Ollama o LM Studio

Ollama y LM Studio usan archivos `.gguf`. Para convertir `modelos/modificado` hace falta [llama.cpp](https://github.com/ggml-org/llama.cpp):

```
python llama.cpp/convert_hf_to_gguf.py modelos/modificado --outtype f16 --outfile modificado-f16.gguf
llama-quantize modificado-f16.gguf modificado-Q4_K_M.gguf Q4_K_M
```

Para LM Studio, alcanza con importar el `.gguf`. Para Ollama, creá un archivo `Modelfile` con la línea `FROM ./modificado-Q4_K_M.gguf` y corré `ollama create mi-modelo -f Modelfile`.

## Para tener en cuenta

- Heretic saca los rechazos, pero no le agrega conocimiento al modelo, y puede equivocarse con la misma seguridad con que antes se negaba. Para salud, plata o temas legales, usalo como punto de partida y no como verdad.
- El modelo modificado sigue bajo la licencia del original (Qwen, Gemma, etc.). Heretic es AGPL-3.0.
