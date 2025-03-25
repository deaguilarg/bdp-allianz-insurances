import streamlit as st
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ctransformers import AutoModelForCausalLM
import os
import time

class RAGSimple:
    def __init__(self, modo_prueba=False):
        # Cargar el modelo de lenguaje
        modelo_path = "llama-2-7b-chat.Q4_K_M.gguf"
        if not os.path.exists(modelo_path):
            raise FileNotFoundError(f"❌ No se encontró el modelo en {modelo_path}")
            
        print("🔄 Cargando modelos...")
        self.llm = AutoModelForCausalLM.from_pretrained(
            modelo_path,
            model_type="llama",
            gpu_layers=20,     # Más capas en GPU por menor uso de memoria (~100MB por capa)
            context_length=512 if modo_prueba else 1024,  # Contexto reducido en modo prueba
            threads=6,         # Balanceado para CPU/GPU
            top_k=40,         # Mantener calidad de búsqueda
            batch_size=2      # Aumentado por menor uso de memoria
        )
        
        # Cargar el modelo de embeddings
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Cargar índice FAISS y textos si existen
        if os.path.exists("vector_index.faiss"):
            self.index = faiss.read_index("vector_index.faiss")
            self.texts = np.load("vector_texts.npy").tolist()
            print("✅ Base de datos vectorial cargada")
        else:
            raise FileNotFoundError("❌ No se encontró la base de datos vectorial")
        
        # Modo prueba para respuestas más cortas
        self.modo_prueba = modo_prueba

    def buscar_contexto(self, pregunta, num_resultados=1):
        """Busca los documentos más relevantes para la pregunta."""
        inicio = time.time()
        # Generar embedding de la pregunta
        question_embedding = self.embedding_model.encode([pregunta])[0]
        tiempo_embedding = time.time() - inicio
        
        # Buscar documentos similares
        inicio_busqueda = time.time()
        D, I = self.index.search(question_embedding.reshape(1, -1), num_resultados)
        tiempo_busqueda = time.time() - inicio_busqueda
        
        # Obtener los textos relevantes
        contexto = "\n".join([self.texts[i] for i in I[0]])
        print(f"⏱️ Tiempo de generación de embedding: {tiempo_embedding:.2f}s")
        print(f"⏱️ Tiempo de búsqueda FAISS: {tiempo_busqueda:.2f}s")
        return contexto

    def generar_respuesta(self, pregunta):
        """Genera una respuesta usando RAG."""
        try:
            inicio_total = time.time()
            # Obtener contexto relevante
            print("🔍 Buscando información relevante...")
            inicio_contexto = time.time()
            contexto = self.buscar_contexto(pregunta, num_resultados=1 if self.modo_prueba else 3)
            tiempo_contexto = time.time() - inicio_contexto
            
            # Crear el prompt con el contexto
            prompt = f"""<s>[INST] <<SYS>>
            You are an AI-powered insurance assistant specifically created to support Allianz advisors. Your role is to deliver clear, accurate, concise, and personalized insurance recommendations (initially Motorcycle and Community insurance). 
            {'Keep responses very short and simple for testing.' if self.modo_prueba else 'Follow these instructions:'} 
            Clearly state your role: "As an Allianz Insurance Assistant, my recommendation is…" 
            Use structured, concise, and relevant responses (max 100 words). 
            Base your answers exclusively on the provided context; if insufficient, clearly indicate this. 
            Suggest actionable follow-up questions advisors should ask customers for more precise recommendations. 
            Maintain a professional yet friendly tone appropriate for Allianz advisors. 
            Clearly acknowledge if you lack information to provide a precise answer. 
            Include the following disclaimer in all responses: 
            "This recommendation is intended to assist Allianz advisors and is for informational purposes only. Customers should refer to the complete policy terms or consult an Allianz representative for a personalized quote."
            <</SYS>>
            
            Contexto: {contexto}
            
            Pregunta: {pregunta} [/INST]"""

            print("🤖 Generando respuesta...")
            inicio_generacion = time.time()
            respuesta = self.llm(
                prompt,
                max_new_tokens=100 if self.modo_prueba else 215,  # Tokens reducidos en modo prueba
                temperature=0.7,
                top_k=40,
                top_p=0.95,
                repetition_penalty=1.1,
                batch_size=2,  # Aumentado por menor uso de memoria
                stop=["</s>", "[INST]"]
            )
            tiempo_generacion = time.time() - inicio_generacion
            
            tiempo_total = time.time() - inicio_total
            print(f"⏱️ Tiempo total de generación de respuesta: {tiempo_total:.2f}s")
            print(f"⏱️ Tiempo de búsqueda de contexto: {tiempo_contexto:.2f}s")
            print(f"⏱️ Tiempo de generación LLM: {tiempo_generacion:.2f}s")

            return respuesta.split("[/INST]")[-1].strip()

        except Exception as e:
            return f"❌ Error al generar respuesta: {str(e)}"

def main():
    st.set_page_config(page_title="Sistema RAG de Documentos", layout="wide")
    
    st.title("🤖 Asistente de Documentos con Llama 2")
    st.write("Haz preguntas sobre tus documentos y obtén respuestas basadas en su contenido.")
    
    # Verificar si existe el modelo
    model_path = "llama-2-7b-chat.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        st.error("⚠️ No se encontró el modelo de Llama 2.")
        st.info(f"Asegúrate de que el archivo {model_path} esté en el directorio.")
        return
    
    # Inicializar el sistema RAG
    try:
        modo_prueba = st.checkbox("¿Deseas usar el modo de prueba?")
        rag = RAGSimple(modo_prueba)
        st.success("✅ Modelo cargado correctamente")
    except FileNotFoundError as e:
        st.error("❌ No se encontraron los archivos necesarios.")
        st.info("Asegúrate de haber ejecutado loader.py primero y de tener el modelo descargado.")
        st.error(f"Error específico: {str(e)}")
        return
    except Exception as e:
        st.error(f"❌ Error al cargar el modelo: {str(e)}")
        return
    
    # Input para la pregunta
    query = st.text_input("💭 Hazme una pregunta sobre tus documentos:")
    
    if query:
        with st.spinner("🔄 Procesando tu pregunta..."):
            try:
                response = rag.generar_respuesta(query)
                
                # Mostrar la respuesta
                st.write("### 📝 Respuesta:")
                st.write(response)
            except Exception as e:
                st.error(f"❌ Error al generar la respuesta: {str(e)}")
                st.info("Intenta reformular tu pregunta o contacta al administrador si el error persiste.")

if __name__ == "__main__":
    main()