import os
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import re

class DocumentProcessor:
    def __init__(self, chunk_size=512, chunk_overlap=0.1):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def create_chunks(self, text):
        """Divide el texto en chunks con overlap."""
        # Limpiar el texto
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split()
        
        # Calcular el overlap en palabras
        overlap_size = int(self.chunk_size * self.chunk_overlap)
        stride = self.chunk_size - overlap_size
        
        chunks = []
        for i in range(0, len(words), stride):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk:  # Asegurarse de que el chunk no esté vacío
                # Añadir metadata al chunk
                chunk_info = {
                    'text': chunk,
                    'start_idx': i,
                    'size': len(chunk.split()),
                }
                chunks.append(chunk_info)
        
        return chunks

    def process_pdf(self, pdf_path):
        """Procesa un archivo PDF y retorna sus chunks."""
        try:
            doc = fitz.open(pdf_path)
            text_chunks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Crear chunks para esta página
                page_chunks = self.create_chunks(text)
                
                # Añadir información de la página a cada chunk
                for chunk in page_chunks:
                    chunk['page'] = page_num + 1
                    chunk['source'] = os.path.basename(pdf_path)
                    text_chunks.extend([chunk['text']])
            
            return text_chunks
            
        except Exception as e:
            print(f"Error procesando {pdf_path}: {str(e)}")
            return []

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

def main():
    # Configuración
    data_dir = "data"
    chunk_size = 512  # Tamaño mediano por defecto
    chunk_overlap = 0.15  # 15% de overlap
    
    # Inicializar procesador
    processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Procesar documentos
    all_chunks = []
    pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    
    print(f"🔍 Procesando {len(pdf_files)} documentos...")
    for pdf_file in tqdm(pdf_files):
        pdf_path = os.path.join(data_dir, pdf_file)
        chunks = processor.process_pdf(pdf_path)
        all_chunks.extend(chunks)
    
    print(f"✅ Se generaron {len(all_chunks)} chunks")
    
    # Generar embeddings
    print("🔄 Generando embeddings...")
    embeddings = processor.embedding_model.encode(all_chunks, show_progress_bar=True)
    
    # Crear índice FAISS
    print("🔄 Creando índice FAISS...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    # Guardar resultados
    print("💾 Guardando archivos...")
    faiss.write_index(index, "vector_index.faiss")
    np.save("vector_texts.npy", all_chunks)
    
    print("✅ Proceso completado")
    print(f"📊 Estadísticas:")
    print(f"- Documentos procesados: {len(pdf_files)}")
    print(f"- Chunks generados: {len(all_chunks)}")
    print(f"- Tamaño de chunk: {chunk_size}")
    print(f"- Overlap: {chunk_overlap*100}%")

if __name__ == "__main__":
    main()
