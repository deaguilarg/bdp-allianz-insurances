@echo off
if not exist "venv\Scripts\activate.bat" (
    echo Error: No se encontró el entorno virtual.
    echo Por favor, ejecuta primero setup_env.bat
    pause
    exit /b 1
)

echo Activando entorno virtual...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Error al activar el entorno virtual
    pause
    exit /b 1
)

echo Ejecutando loader.py...
python loader.py
pause 