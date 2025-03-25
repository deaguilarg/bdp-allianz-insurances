import json
import os
from typing import List, Dict, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import numpy as np
from datetime import datetime
import fitz

class EnhancedRetriever:
    def __init__(self, metadata_file="documentos_metadata.json", data_dir="preparsed_data"):
        self.data_dir = data_dir
        self.metadata_file = metadata_file
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self.metadata = self._load_metadata()
        self.vector_store = None

    def _load_metadata(self) -> Dict:
        """Carga los metadatos del archivo JSON."""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando metadatos: {str(e)}")
            return {}

    def _enhance_chunk_with_metadata(self, chunk: str, pdf_path: str) -> Dict:
        """Enriquece el chunk con metadatos relevantes."""
        filename = os.path.basename(pdf_path)
        doc_metadata = self.metadata.get(filename, {})
        
        # Extraer información relevante de los metadatos
        insurance_terms = doc_metadata.get('content_summary', {}).get('insurance_terms_present', [])
        main_sections = doc_metadata.get('content_summary', {}).get('main_sections', [])
        
        # Determinar si el chunk contiene términos de seguros
        contains_insurance_terms = any(term in chunk.lower() for term in insurance_terms)
        
        # Determinar si el chunk es parte de una sección importante
        in_important_section = any(section in chunk for section in main_sections)
        
        # Calcular un score de relevancia basado en metadatos
        relevance_score = 1.0
        if contains_insurance_terms:
            relevance_score *= 1.5
        if in_important_section:
            relevance_score *= 1.3
        
        return {
            'content': chunk,
            'source': filename,
            'insurance_terms_present': contains_insurance_terms,
            'in_important_section': in_important_section,
            'relevance_score': relevance_score,
            'doc_title': doc_metadata.get('document_info', {}).get('title', ''),
            'section_context': next((s for s in main_sections if s in chunk), '')
        }

    def process_documents(self):
        """Procesa los documentos y crea el índice de vectores."""
        all_chunks = []
        
        print("🔍 Procesando documentos para retrieval...")
        for filename, doc_metadata in self.metadata.items():
            pdf_path = os.path.join(self.data_dir, filename)
            try:
                # Extraer texto del PDF
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                
                # Dividir en chunks
                chunks = self.text_splitter.split_text(text)
                
                # Enriquecer cada chunk con metadatos
                for chunk in chunks:
                    enhanced_chunk = self._enhance_chunk_with_metadata(chunk, pdf_path)
                    all_chunks.append(enhanced_chunk)
                
                print(f"✅ Procesado: {filename}")
                
            except Exception as e:
                print(f"❌ Error procesando {filename}: {str(e)}")
                continue
        
        # Crear índice de vectores
        texts = [chunk['content'] for chunk in all_chunks]
        metadatas = all_chunks
        
        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
        print(f"\n✅ Índice de vectores creado con {len(all_chunks)} chunks")

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Realiza la búsqueda considerando tanto similitud semántica como metadatos."""
        if not self.vector_store:
            print("❌ Primero debes procesar los documentos con process_documents()")
            return []
        
        # Realizar búsqueda semántica
        results = self.vector_store.similarity_search_with_score(query, k=k*2)  # Obtenemos más resultados para filtrar
        
        # Reordenar resultados considerando tanto similitud como metadata
        enhanced_results = []
        for doc, score in results:
            metadata = doc.metadata
            final_score = (1 / (1 + score)) * metadata['relevance_score']
            
            enhanced_results.append({
                'content': doc.page_content,
                'metadata': metadata,
                'final_score': final_score
            })
        
        # Ordenar por score final y tomar los k mejores
        enhanced_results.sort(key=lambda x: x['final_score'], reverse=True)
        return enhanced_results[:k]

    def save_index(self, path: str = "vector_store"):
        """Guarda el índice de vectores."""
        if self.vector_store:
            self.vector_store.save_local(path)
            print(f"✅ Índice guardado en {path}")
    
    def load_index(self, path: str = "vector_store"):
        """Carga un índice de vectores existente."""
        if os.path.exists(path):
            self.vector_store = FAISS.load_local(path, self.embeddings)
            print(f"✅ Índice cargado desde {path}")

def main():
    # Ejemplo de uso
    retriever = EnhancedRetriever()
    
    # Procesar documentos y crear índice
    retriever.process_documents()
    
    # Guardar índice para uso futuro
    retriever.save_index()
    
    # Ejemplo de búsqueda
    query = "¿Cuáles son las coberturas principales?"
    results = retriever.retrieve(query)
    
    print(f"\n🔍 Resultados para: '{query}'")
    for i, result in enumerate(results, 1):
        print(f"\n--- Resultado {i} (Score: {result['final_score']:.3f}) ---")
        print(f"Documento: {result['metadata']['doc_title']}")
        if result['metadata']['section_context']:
            print(f"Sección: {result['metadata']['section_context']}")
        print(f"Contenido: {result['content'][:200]}...")

if __name__ == "__main__":
    main() 