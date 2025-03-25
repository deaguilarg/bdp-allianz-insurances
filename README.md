# Sistema RAG para Documentación de Seguros Allianz

Este proyecto implementa un sistema de Recuperación Aumentada de Generación (RAG) para procesar y consultar documentación de seguros utilizando Llama 2 y una base de datos vectorial.

## 🏗️ Estructura del Proyecto

```
.
├── data/                    # Directorio para documentos PDF y TXT
├── loader.py               # Procesador de documentos y creación de índices
├── RAG.py                 # Sistema RAG principal
├── db_viewer.py           # Visualizador web de la base de datos vectorial
├── test_llama.py          # Script de prueba para el modelo Llama 2
└── requirements.txt       # Dependencias del proyecto
```

## 📋 Requisitos

1. Python 3.8+
2. Modelo Llama 2: `llama-2-7b-chat.Q5_K_S.gguf` (se descarga automáticamente con `download_model.py`)
3. Dependencias Python listadas en `requirements.txt`

## 🚀 Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Descargar el modelo Llama 2:
```bash
python download_model.py
```
Este script descargará automáticamente el modelo `llama-2-7b-chat.Q5_K_S.gguf` desde Hugging Face.
- Tamaño aproximado: 4.65GB
- Tiempo estimado de descarga: 5-10 minutos (dependiendo de la conexión)
- Asegúrate de tener suficiente espacio en disco (mínimo 5GB)

Alternativamente, puedes descargar manualmente el modelo desde:
https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF/resolve/main/llama-2-7b-chat.Q5_K_S.gguf

## 💾 Preparación de Datos

1. Colocar los documentos PDF/TXT en la carpeta `data/`
2. Ejecutar el procesador de documentos:
```bash
python loader.py
```

## 🔍 Uso del Sistema

### Visualizar Base de Datos
```bash
streamlit run db_viewer.py
```
- Ver todos los fragmentos indexados
- Realizar búsquedas semánticas
- Explorar el contenido procesado

### Usar el Sistema RAG
```bash
python RAG.py
```
- Hacer preguntas sobre la documentación
- Obtener respuestas basadas en el contexto
- Interactuar con el modelo Llama 2

### Probar el Modelo
```bash
python test_llama.py
```
- Verificar el funcionamiento básico del modelo
- Realizar pruebas simples de generación

## 🔄 Flujo de Trabajo

1. **Procesamiento de Documentos** (`loader.py`):
   - Carga documentos PDF/TXT
   - Divide en secciones relevantes
   - Genera embeddings
   - Crea índice vectorial FAISS

2. **Base de Datos Vectorial**:
   - Almacena fragmentos de texto
   - Mantiene índices para búsqueda rápida
   - Permite búsquedas semánticas

3. **Sistema RAG** (`RAG.py`):
   - Recibe preguntas del usuario
   - Busca contexto relevante
   - Genera respuestas usando Llama 2

## 📊 Componentes Principales

### Loader (`loader.py`)
- Clase `DocumentProcessor`
- Manejo de múltiples formatos
- Procesamiento de texto inteligente
- Generación de embeddings

### RAG (`RAG.py`)
- Clase `RAGSimple`
- Integración con Llama 2
- Búsqueda de contexto
- Generación de respuestas

### Visualizador (`db_viewer.py`)
- Interfaz web con Streamlit
- Exploración de datos
- Búsqueda semántica
- Visualización de fragmentos

## 🛠️ Configuración

- Modelo: CPU por defecto (cambiar `gpu_layers=0` para GPU)
- Contexto: 2048 tokens máximo
- Threads: 4 (ajustable según CPU)
- Fragmentos: ~1000 caracteres por sección

## 📝 Notas

- Los documentos deben estar en la carpeta `data/`
- El modelo Llama 2 debe estar en el directorio raíz
- Se recomienda usar GPU para mejor rendimiento
- La base de datos vectorial se actualiza al procesar nuevos documentos

## 📄 Licencia

Este proyecto es privado y para uso interno. 