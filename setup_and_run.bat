@echo off
chcp 65001 > nul

echo 🚀 Iniciando configuración del sistema RAG...

:: Verificar si Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor, instálalo antes de continuar.
    pause
    exit /b 1
)

:: Limpiar instalación anterior si existe
if exist "venv" (
    echo 🧹 Limpiando instalación anterior...
    rmdir /s /q venv
)

:: Crear y activar entorno virtual
echo 🔧 Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate.bat

:: Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

:: Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt

:: Crear directorio para datos si no existe
echo 📁 Creando directorio para documentos...
if not exist "data" mkdir data

:: Descargar modelo de Llama 2
echo 🔄 Descargando modelo Llama 2...
python -c "from huggingface_hub import hf_hub_download; hf_hub_download('TheBloke/Llama-2-7B-Chat-GGUF', 'llama-2-7b-chat.q4_k_m.gguf', local_dir='.')"

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

:: Iniciar la interfaz de Streamlit
echo 🌐 Iniciando la interfaz web...
streamlit run RAG.py

pause 