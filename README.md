# Sistema RAG para Análisis de Documentos de Seguros

Este proyecto implementa un sistema de Retrieval-Augmented Generation (RAG) optimizado para el análisis y consulta de documentos de seguros.

## Requisitos

```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
.
├── RAG.py              # Script principal del sistema RAG
├── test_rag.py         # Script para pruebas de rendimiento
├── data_wrangler.py    # Herramienta de análisis de PDFs
├── preparsed_data/     # Directorio para documentos PDF
└── requirements.txt    # Dependencias del proyecto
```

## Uso del Sistema RAG

1. **Preparación**:
   - Coloca tus archivos PDF en el directorio `preparsed_data/`
   - Activa el entorno virtual:
     ```bash
     .\venv\Scripts\activate  # Windows
     source venv/bin/activate # Linux/Mac
     ```

2. **Análisis de Documentos**:
   ```bash
   python data_wrangler.py
   ```
   Este comando analizará los PDFs y generará visualizaciones útiles.

3. **Consultas al Sistema**:
   ```bash
   python RAG.py
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