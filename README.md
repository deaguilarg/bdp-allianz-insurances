# Sistema RAG para Análisis de Documentos de Seguros

Este proyecto implementa un sistema de Retrieval-Augmented Generation (RAG) optimizado para el análisis y consulta de documentos de seguros.

## Configuración Inicial

1. **Configurar el Entorno Virtual**:
   ```bash
   setup_env.bat
   ```
   Este script:
   - Crea un entorno virtual
   - Instala todas las dependencias necesarias

2. **Descargar el Modelo**:
   ```bash
   python model_downloader.py
   ```
   Este script descargará automáticamente el modelo necesario para el sistema.

3. **Procesar Documentos**:
   ```bash
   run_loader.bat
   ```
   Procesa los documentos PDF en el directorio `preparsed_data/` y crea el índice vectorial.

## Estructura del Proyecto

```
.
├── RAG.py              # Script principal del sistema RAG
├── loader.py           # Procesador de documentos
├── db_viewer.py        # Visualizador de la base de datos
├── data_wrangler.py    # Analizador de PDFs
├── model_downloader.py # Descargador del modelo
├── preparsed_data/     # Directorio para documentos PDF
├── setup_env.bat       # Script de configuración del entorno
├── run_loader.bat      # Script para ejecutar el loader
├── run_rag.bat         # Script para ejecutar el RAG
├── run_db_viewer.bat   # Script para ejecutar el visualizador
└── requirements.txt    # Dependencias del proyecto
```

## Uso del Sistema

Una vez completada la configuración inicial, puedes usar cualquiera de estas herramientas:

1. **Sistema RAG** (Consultas):
   ```bash
   run_rag.bat
   ```
   Para hacer preguntas sobre los documentos y obtener respuestas.

2. **Visualizador de Base de Datos**:
   ```bash
   run_db_viewer.bat
   ```
   - Interfaz web para explorar los documentos indexados
   - Realizar búsquedas semánticas
   - Visualizar fragmentos de texto

3. **Análisis de PDFs**:
   ```bash
   python data_wrangler.py
   ```
   - Analiza la estructura de los documentos
   - Genera estadísticas y visualizaciones
   - Identifica patrones y términos clave

## Parámetros Configurables

En `RAG.py`:
- `chunk_size`: Tamaño de los fragmentos de texto (default: 500)
- `chunk_overlap`: Superposición entre fragmentos (default: 50)
- `top_k`: Número de resultados a recuperar (default: 4)

## Componentes Principales

1. **Loader** (`run_loader.bat`):
   - Procesa los documentos PDF
   - Genera embeddings
   - Crea el índice vectorial

2. **Visualizador** (`run_db_viewer.bat`):
   - Interfaz web para explorar documentos
   - Búsqueda semántica
   - Visualización de fragmentos

3. **Sistema RAG** (`run_rag.bat`):
   - Consultas en lenguaje natural
   - Recuperación de contexto relevante
   - Generación de respuestas

4. **Analizador de PDFs** (`data_wrangler.py`):
   - Análisis de estructura
   - Estadísticas de contenido
   - Visualizaciones

## Notas Importantes

- El sistema está optimizado para documentos en español
- Se recomienda usar GPU para mejor rendimiento
- Los documentos deben estar en formato PDF
- El sistema maneja automáticamente la memoria para documentos grandes

## Solución de Problemas

1. **Entorno Virtual**:
   - Asegúrate de que `setup_env.bat` se ejecutó correctamente
   - Verifica que todas las dependencias se instalaron
   - El entorno virtual debe estar activado para ejecutar los scripts

2. **Modelo**:
   - Confirma que `model_downloader.py` completó la descarga
   - Verifica que el modelo está en la ubicación correcta
   - Asegúrate de tener suficiente espacio en disco

3. **Procesamiento de Documentos**:
   - Los PDFs deben estar en `preparsed_data/`
   - Ejecuta `run_loader.bat` cada vez que agregues nuevos documentos
   - Verifica que los archivos PDF son legibles y no están corruptos

4. **Rendimiento**:
   - Ajusta `chunk_size` para documentos grandes
   - Verifica la disponibilidad de GPU
   - Ajusta `top_k` según necesidades

5. **Calidad de Respuestas**:
   - Ajusta el prompt según el dominio específico
   - Modifica los parámetros de chunking
   - Verifica la calidad de los documentos fuente

## Análisis de Documentos

El script `data_wrangler.py` proporciona:
- Análisis de estructura de documentos
- Estadísticas de contenido
- Visualizaciones de datos
- Análisis de términos de seguros

## Pruebas de Rendimiento

Para ejecutar pruebas de rendimiento:
```bash
python test_rag.py
```

## Análisis de Documentos

El script `data_wrangler.py` proporciona:
- Análisis de estructura de documentos
- Estadísticas de contenido
- Visualizaciones de datos
- Análisis de términos de seguros

## Notas Importantes

- El sistema está optimizado para documentos en español
- Se recomienda usar GPU para mejor rendimiento
- Los documentos deben estar en formato PDF
- El sistema maneja automáticamente la memoria para documentos grandes

## Solución de Problemas

1. **Uso de Memoria**:
   - Ajusta `chunk_size` para documentos grandes
   - Utiliza el modo batch para procesar grandes volúmenes

2. **Rendimiento**:
   - Verifica la disponibilidad de GPU
   - Ajusta `top_k` según necesidades

3. **Calidad de Respuestas**:
   - Ajusta el prompt según el dominio específico
   - Modifica los parámetros de chunking 