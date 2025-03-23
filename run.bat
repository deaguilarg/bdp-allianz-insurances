@echo off
chcp 65001 > nul

:: Activar el entorno virtual
call venv\Scripts\activate.bat

:: Verificar si existen los archivos necesarios
if not exist "vector_index.faiss" (
    echo ❌ No se encontró la base de datos vectorial. Necesitas procesar los documentos primero.
    echo 🔄 Procesando documentos...
    python loader.py
)

:: Iniciar la interfaz
echo 🌐 Iniciando la interfaz web...
streamlit run RAG.py

pause 