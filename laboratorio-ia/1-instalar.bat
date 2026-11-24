@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo.
echo === Laboratorio de IA: instalacion ===
echo.

where nvidia-smi >nul 2>nul
if errorlevel 1 (
  echo [!] No encuentro el driver de NVIDIA. Instalalo o actualizalo desde nvidia.com y volve a probar.
  pause
  exit /b 1
)
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo.

set "PY="
py -3.12 --version >nul 2>nul && set "PY=py -3.12"
if not defined PY py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY python --version >nul 2>nul && set "PY=python"
if not defined PY (
  echo [!] Falta Python. Instala Python 3.12 desde https://www.python.org/downloads/
  echo     y marca la opcion "Add python.exe to PATH". Despues volve a correr este archivo.
  pause
  exit /b 1
)

if not exist .venv\Scripts\activate.bat (
  echo Creando entorno de Python en .venv ...
  %PY% -m venv .venv
  if errorlevel 1 goto :error
)
call .venv\Scripts\activate.bat
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
  echo [!] Necesitas Python 3.10 o mas nuevo. Borra la carpeta .venv, instala Python 3.12 y volve a probar.
  pause
  exit /b 1
)

python -m pip install -U pip
echo.
echo Instalando PyTorch con soporte para tu placa (son ~3 GB, puede tardar)...
rem Si tu placa es una GTX 10xx o mas vieja, cambia cu128 por cu126 en la linea de abajo.
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
if errorlevel 1 goto :error

echo.
echo Instalando Heretic...
pip install -U heretic-llm
if errorlevel 1 goto :error

echo.
python -c "import torch, sys; ok = torch.cuda.is_available(); print('PyTorch', torch.__version__, '- GPU:', torch.cuda.get_device_name(0) if ok else 'NO DETECTADA'); sys.exit(0 if ok else 3)"
if errorlevel 3 (
  echo [!] PyTorch no ve la GPU. Actualiza el driver de NVIDIA y volve a correr este archivo.
  pause
  exit /b 1
)
echo.
echo Todo instalado. Siguiente paso: 2-correr-heretic.bat
pause
exit /b 0

:error
echo.
echo [!] Algo fallo. Copia el mensaje de error de arriba y pasamelo.
pause
exit /b 1
