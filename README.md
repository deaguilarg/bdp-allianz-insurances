# Sistema RAG para Análisis de Documentos de Seguros

Este proyecto implementa un sistema de Retrieval-Augmented Generation (RAG) optimizado para el análisis y consulta de documentos de seguros.

## Instalación Rápida

1. Ejecuta el script de instalación:
   ```bash
   install.bat
   ```
   Este script:
   - Crea un entorno virtual
   - Instala todas las dependencias
   - Descarga los modelos necesarios

## Estructura del Proyecto

```
.
├── RAG.py              # Script principal del sistema RAG
├── loader.py           # Procesador de documentos
├── db_viewer.py        # Visualizador de la base de datos
├── preparsed_data/     # Directorio para documentos PDF
├── install.bat         # Script de instalación
├── run_loader.bat      # Script para ejecutar el loader
├── run_rag.bat         # Script para ejecutar el RAG
├── run_viewer.bat      # Script para ejecutar el visualizador
└── requirements.txt    # Dependencias del proyecto
```

## Uso del Sistema

1. **Preparación de Documentos**:
   - Coloca tus archivos PDF en el directorio `preparsed_data/`
   - Ejecuta el procesador de documentos:
     ```bash
     run_loader.bat
     ```

2. **Visualizar Base de Datos**:
   - Para explorar los documentos procesados:
     ```bash
     run_viewer.bat
     ```
   - Se abrirá una interfaz web donde podrás:
     - Ver todos los documentos indexados
     - Realizar búsquedas semánticas
     - Explorar el contenido procesado

3. **Usar el Sistema RAG**:
   - Para hacer consultas al sistema:
     ```bash
     run_rag.bat
     ```

## Parámetros Configurables

En `RAG.py`:
- `chunk_size`: Tamaño de los fragmentos de texto (default: 500)
- `chunk_overlap`: Superposición entre fragmentos (default: 50)
- `top_k`: Número de resultados a recuperar (default: 4)

## Optimización de Rendimiento

El sistema está optimizado para:
- Uso eficiente de GPU cuando está disponible
- Caché de embeddings para consultas frecuentes
- Procesamiento por lotes para mejor rendimiento

## Componentes Principales

1. **Loader** (`run_loader.bat`):
   - Procesa los documentos PDF
   - Genera embeddings
   - Crea el índice vectorial

2. **Visualizador** (`run_viewer.bat`):
   - Interfaz web para explorar documentos
   - Búsqueda semántica
   - Visualización de fragmentos

3. **Sistema RAG** (`run_rag.bat`):
   - Consultas en lenguaje natural
   - Recuperación de contexto relevante
   - Generación de respuestas

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

4. **Problemas con los Scripts .bat**:
   - Asegúrate de que el entorno virtual está creado correctamente
   - Verifica que todos los modelos se descargaron durante la instalación
   - Comprueba que los archivos PDF están en el directorio correcto

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