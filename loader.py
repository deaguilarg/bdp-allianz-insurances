import os
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class DocumentProcessor:
    def __init__(self, data_directory):
        # Verificar que el directorio existe
        if not os.path.exists(data_directory):
            raise FileNotFoundError(f"El directorio {data_directory} no existe")
        
        self.data_directory = data_directory
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def dataLoader(self):
        """Carga y extrae texto de archivos PDF y TXT."""
        # Obtener lista de archivos
        all_files = [f for f in os.listdir(self.data_directory) 
                    if f.endswith(('.pdf', '.txt'))]
        
        if not all_files:
            print("⚠️ No se encontraron archivos PDF o TXT en el directorio.")
            return [], []
        
        texts = []
        doc_ids = []
        
        for file in all_files:
            file_path = os.path.join(self.data_directory, file)
            try:
                if file.endswith('.pdf'):
                    # Extraer texto del PDF
                    text = ""
                    with fitz.open(file_path) as doc:
                        for page in doc:
                            text += page.get_text("text") + "\n"
                else:
                    # Leer archivo TXT
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                
                if not text.strip():
                    print(f"⚠️ No se pudo extraer texto de {file}")
                    continue
                    
                texts.append(text)
                doc_ids.append(file)
                print(f"✅ Procesado: {file}")
                
            except Exception as e:
                print(f"❌ Error procesando {file}: {str(e)}")
                continue
            
        return texts, doc_ids

    def splitter(self, texts, doc_ids):
        """Divide los textos en párrafos."""
        split_texts = []
        split_ids = []
        
        for text, doc_id in zip(texts, doc_ids):
            # Limpiar el texto
            text = text.replace('\r', '\n')
            
            # Dividir por secciones si hay títulos en mayúsculas
            if doc_id.endswith('.txt'):
                sections = []
                current_section = []
                lines = text.split('\n')
                
                for line in lines:
                    if line.isupper() and len(line) > 10:  # Probable título de sección
                        if current_section:
                            sections.append('\n'.join(current_section))
                        current_section = [line]
                    else:
                        current_section.append(line)
                
                if current_section:
                    sections.append('\n'.join(current_section))
                
                # Si no se encontraron secciones, usar párrafos
                if not sections:
                    sections = text.split('\n\n')
            else:
                # Para PDFs usar la división por párrafos original
                sections = text.split('\n\n')
            
            # Procesar cada sección/párrafo
            for i, section in enumerate(sections):
                # Limpiar espacios y saltos de línea extras
                clean_section = ' '.join(section.split())
                
                # Filtrar secciones válidas
                if len(clean_section) > 50 and any(c.isalpha() for c in clean_section):
                    split_texts.append(clean_section)
                    split_ids.append(f"{doc_id} | sección {i+1}")
            
            print(f"📄 {doc_id}: {len(sections)} secciones extraídas")
                
        if not split_texts:
            print("⚠️ No se pudo extraer ninguna sección válida de los documentos")
        else:
            print(f"✅ Total de secciones extraídas: {len(split_texts)}")
            
        return split_texts, split_ids

    def embedder(self, texts):
        """Genera embeddings para los textos."""
        if not texts:
            raise ValueError("No hay textos para generar embeddings")
            
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            raise Exception(f"Error generando embeddings: {str(e)}")

    def indexer(self, embeddings, split_ids, split_texts):
        """Crea y guarda el índice FAISS junto con los IDs y textos."""
        if len(embeddings) != len(split_ids) or len(embeddings) != len(split_texts):
            raise ValueError("La cantidad de embeddings, IDs y textos no coincide")
            
        try:
            # Crear índice FAISS
            embedding_dim = embeddings.shape[1]
            index = faiss.IndexFlatL2(embedding_dim)
            index.add(embeddings)

            # Guardar índice y metadatos
            faiss.write_index(index, "vector_index.faiss")
            np.save("vector_ids.npy", np.array(split_ids))
            np.save("vector_texts.npy", np.array(split_texts))

            print(f"✅ Se han indexado {len(split_ids)} fragmentos en FAISS.")
            
        except Exception as e:
            raise Exception(f"Error en la indexación: {str(e)}")

    def process_documents(self):
        """Ejecuta el pipeline completo de procesamiento."""
        try:
            print("🔄 Iniciando procesamiento de documentos...")
            
            print("📚 Cargando documentos...")
            texts, doc_ids = self.dataLoader()
            
            if not texts:
                return "❌ No hay documentos para procesar"
            
            print("✂️ Dividiendo textos...")
            split_texts, split_ids = self.splitter(texts, doc_ids)
            
            if not split_texts:
                return "❌ No se generaron fragmentos de texto válidos"
            
            print("🧮 Generando embeddings...")
            embeddings = self.embedder(split_texts)
            
            print("💾 Indexando en FAISS...")
            self.indexer(embeddings, split_ids, split_texts)
            
            return "✅ Procesamiento completado con éxito"
            
        except Exception as e:
            print(f"❌ Error en el procesamiento: {str(e)}")
            return "❌ El proceso falló"

if __name__ == "__main__":
    try:
        processor = DocumentProcessor("data")
        result = processor.process_documents()
        print(f"\nResultado final: {result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
