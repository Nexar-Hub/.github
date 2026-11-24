#!/usr/bin/env bash
# Instalación para Linux con placa NVIDIA.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v nvidia-smi >/dev/null; then
  echo "[!] No encuentro el driver de NVIDIA (nvidia-smi). Instalalo y volvé a probar."
  exit 1
fi
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

PY=${PYTHON:-python3}
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
  echo "[!] Necesitás Python 3.10 o más nuevo."; exit 1; }

[ -d .venv ] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip
# Si tu placa es una GTX 10xx o más vieja, cambiá cu128 por cu126.
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -U heretic-llm
python -c "import torch, sys; ok = torch.cuda.is_available(); print('PyTorch', torch.__version__, '- GPU:', torch.cuda.get_device_name(0) if ok else 'NO DETECTADA'); sys.exit(0 if ok else 3)"
echo "Todo instalado. Siguiente paso: ./correr-heretic.sh"
