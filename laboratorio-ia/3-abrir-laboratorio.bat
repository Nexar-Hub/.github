@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
  echo Primero corre 1-instalar.bat
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
echo Cargando los modelos... se abre el navegador solo. Para cerrar el laboratorio, cerra esta ventana.
python lab\servidor.py %*
pause
