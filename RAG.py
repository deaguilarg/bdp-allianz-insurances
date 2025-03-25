import streamlit as st
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ctransformers import AutoModelForCausalLM
import os

class RAGSimple:
    def __init__(self):
        # Cargar el modelo de lenguaje
        modelo_path = "llama-2-7b-chat.q4_k_m.gguf"
        if not os.path.exists(modelo_path):
            raise FileNotFoundError(f"❌ No se encontró el modelo en {modelo_path}")
            
        print("🔄 Cargando modelos...")
        self.llm = AutoModelForCausalLM.from_pretrained(
            modelo_path,
            model_type="llama",
            gpu_layers=0,
            context_length=2048,
            threads=4
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

    def buscar_contexto(self, pregunta, num_resultados=3):
        """Busca los documentos más relevantes para la pregunta."""
        # Generar embedding de la pregunta
        question_embedding = self.embedding_model.encode([pregunta])[0]
        
        # Buscar documentos similares
        D, I = self.index.search(question_embedding.reshape(1, -1), num_resultados)
        
        # Obtener los textos relevantes
        contexto = "\n".join([self.texts[i] for i in I[0]])
        return contexto

    def generar_respuesta(self, pregunta):
        """Genera una respuesta usando RAG."""
        try:
            # Obtener contexto relevante
            print("🔍 Buscando información relevante...")
            contexto = self.buscar_contexto(pregunta)
            
            # Crear el prompt con el contexto
            prompt = f"""<s>[INST] <<SYS>>
            You are an AI-powered insurance assistant specifically created to support Allianz advisors. Your role is to deliver clear, accurate, concise, and personalized insurance recommendations (initially Motorcycle and Community insurance). 

            Follow these instructions: 

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
            respuesta = self.llm(
                prompt,
                max_new_tokens=256,
                temperature=0.7,
                stop=["</s>", "[INST]"]
            )

            return respuesta.split("[/INST]")[-1].strip()

        except Exception as e:
            return f"❌ Error al generar respuesta: {str(e)}"

def main():
    st.set_page_config(page_title="Sistema RAG de Documentos", layout="wide")
    
    st.title("🤖 Asistente de Documentos con Llama 2")
    st.write("Haz preguntas sobre tus documentos y obtén respuestas basadas en su contenido.")
    
    # Verificar si existe el modelo
    model_path = "llama-2-7b-chat.Q5_K_S.gguf"
    if not os.path.exists(model_path):
        st.error("⚠️ No se encontró el modelo de Llama 2.")
        st.info(f"Asegúrate de que el archivo {model_path} esté en el directorio.")
        return
    
    # Inicializar el sistema RAG
    try:
        rag = RAGSimple()
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