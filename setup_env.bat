@echo off
echo Eliminando entorno virtual existente si existe...
if exist venv (
    rmdir /s /q venv
)

echo Creando nuevo entorno virtual...
python -m venv venv

echo Verificando creación del entorno virtual...
if not exist "venv\Scripts\python.exe" (
    echo Error: No se pudo crear el entorno virtual correctamente
    pause
    exit /b 1
)

echo Instalando dependencias...
call "venv\Scripts\python.exe" -m pip install --upgrade pip
call "venv\Scripts\python.exe" -m pip install -r requirements.txt

echo Instalación completada.
pause 