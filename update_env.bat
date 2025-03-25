@echo off
echo Actualizando dependencias del entorno virtual...

:: Activar el entorno virtual
call .\venv\Scripts\activate.bat

:: Actualizar pip
python -m pip install --upgrade pip

:: Actualizar las dependencias existentes
pip install --upgrade -r requirements.txt

:: Instalar/Actualizar el modelo de spaCy para español
python -m spacy download es_core_news_md

:: Verificar instalación
echo.
echo Verificando instalación...
pip list

echo.
echo Actualización completada.
pause 