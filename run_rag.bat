@echo off
if not exist "venv\Scripts\activate" (
    echo Error: No se encontró el entorno virtual.
    echo Por favor, ejecuta primero setup_env.bat
    pause
    exit /b 1
)

echo Activando entorno virtual...
call "venv\Scripts\activate"
if errorlevel 1 (
    echo Error al activar el entorno virtual
    pause
    exit /b 1
)

echo Ejecutando RAG.py con Streamlit...
streamlit run RAG.py
pause 