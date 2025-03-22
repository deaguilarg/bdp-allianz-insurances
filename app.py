import streamlit as st
import os
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# 🔹 Configurar directorio de PDFs
pdf_directory = "data"

# 🔹 Cargar el modelo de embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔹 Cargar el índice FAISS y los IDs de los documentos
index = faiss.read_index("vector_index.faiss")
doc_ids = np.load("vector_ids.npy", allow_pickle=True)  # Cargar los nombres de los archivos indexados

# 🔹 Cargar el modelo de Hugging Face para responder preguntas
nlp = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2",
)

# 🔹 FUNCIÓN PARA RECUPERAR DOCUMENTOS RELEVANTES DESDE "data/"
def retrieve_relevant_documents(query, k=3):
    """Convierte la consulta en embeddings y busca en FAISS los fragmentos más relevantes en la carpeta data/."""
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, k)

    relevant_docs = []
    retrieved_filenames = []

    for idx in indices[0]:  # Iterar sobre los fragmentos más relevantes
        if idx >= len(doc_ids):
            continue
        
        doc_info = doc_ids[idx]  # 🔹 Nombre del PDF + número de párrafo
        pdf_filename, paragraph_id = doc_info.split(" | párrafo ")

        retrieved_filenames.append(pdf_filename)

        # 🔹 Leer el párrafo específico desde el PDF
        pdf_path = os.path.join(pdf_directory, pdf_filename)
        paragraph_id = int(paragraph_id)

        try:
            with fitz.open(pdf_path) as doc:
                text = ""
                paragraph_counter = 0
                for page in doc:
                    paragraphs = page.get_text("text").split("\n\n")  # Dividimos por párrafos
                    for p in paragraphs:
                        if len(p.strip()) > 50:
                            if paragraph_counter == paragraph_id:
                                text = p.strip()
                                break
                            paragraph_counter += 1
        except Exception as e:
            print(f"❌ Error al leer {pdf_filename}: {e}")
            continue

        # Si el párrafo tiene contenido, agregarlo
        if text:
            relevant_docs.append({
                "filename": pdf_filename,
                "paragraph_id": paragraph_id,
                "content": text
            })

    return relevant_docs if relevant_docs else ["No se encontró información relevante."]

# 🔹 FUNCIÓN PARA RESPONDER PREGUNTAS USANDO RETRIEVAL + QA
def query_document_qa(user_query, k=3):
    """Recupera párrafos usando FAISS y responde la pregunta con `deepset/roberta-base-squad2`."""
    retrieved_docs = retrieve_relevant_documents(user_query, k)

    if not retrieved_docs or retrieved_docs == ["No se encontró información relevante."]:
        return "No encontré información relevante.", []

    # 🔹 Concatenar los párrafos recuperados
    context = "\n\n".join([doc["content"] for doc in retrieved_docs])

    # 🔹 Hacer la pregunta al modelo de Hugging Face
    response = nlp(question=user_query, context=context)
    answer = response.get("answer", "No encontré una respuesta clara.")

    return answer, retrieved_docs

# 🔹 INTERFAZ EN STREAMLIT
st.set_page_config(page_title="🔍 RAG - Respuestas con Documentos", layout="wide")
st.title("📚 RAG - Sistema de Respuestas Basado en Documentos")

# 📝 Entrada de usuario
st.markdown("### 📝 Ingresa tu pregunta:")
user_query = st.text_input("Escribe tu pregunta sobre los documentos:")

if st.button("🔍 Buscar Respuesta"):
    if user_query.strip():
        with st.spinner("Buscando respuesta..."):
            response, retrieved_docs = query_document_qa(user_query)

        # 🔹 Mostrar la respuesta generada
        st.success("✅ Respuesta encontrada:")
        st.write(f"**🤖 {response}**")

        # 🔹 Mostrar los documentos relevantes recuperados
        st.markdown("### 📂 Documentos Consultados:")
        if retrieved_docs:
            for doc in retrieved_docs:
                with st.expander(f"📄 {doc['filename']} | Párrafo {doc['paragraph_id']}"):
                    st.write(doc["content"])
        else:
            st.warning("No se encontraron documentos relevantes.")

    else:
        st.warning("⚠️ Por favor ingresa una pregunta.")
