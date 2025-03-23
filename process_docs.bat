@echo off
chcp 65001 > nul

:: Activar el entorno virtual
call venv\Scripts\activate.bat

:: Verificar si hay archivos PDF en el directorio data
dir /b "data\*.pdf" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ No se encontraron archivos PDF en el directorio 'data'.
    echo Por favor, coloca tus archivos PDF en el directorio 'data' antes de continuar.
    echo Presiona cualquier tecla cuando hayas añadido los archivos PDF...
    pause > nul
)

:: Procesar documentos
echo 🔄 Procesando documentos...
python loader.py

echo ✅ Documentos procesados. Puedes ejecutar run.bat para iniciar la interfaz.
pause 