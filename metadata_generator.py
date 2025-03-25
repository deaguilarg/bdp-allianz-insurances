import os
import fitz  # PyMuPDF
import json
from datetime import datetime
import hashlib
from typing import Dict, List
import re
from collections import Counter
import numpy as np

class MetadataGenerator:
    def __init__(self, data_dir="preparsed_data"):
        self.data_dir = data_dir
        self.pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        self.insurance_terms = [
            'póliza', 'prima', 'deducible', 'cobertura', 'exclusiones', 
            'beneficiario', 'asegurado', 'aseguradora', 'siniestro', 
            'indemnización', 'reclamación', 'vigencia', 'renovación', 
            'antigüedad', 'cargas', 'franquicia', 'cláusulas'
        ]

    def extract_text_content(self, pdf_path: str) -> Dict:
        """Extrae y analiza el contenido textual del PDF."""
        doc = fitz.open(pdf_path)
        content = {
            'full_text': '',
            'paragraphs': [],
            'word_frequencies': Counter(),
            'insurance_terms_freq': Counter(),
            'total_words': 0,
            'sections': []
        }

        # Extraer texto completo y por párrafos
        for page in doc:
            # Intentar diferentes métodos de extracción
            text = ""
            # Método 1: Extracción normal
            text_standard = page.get_text()
            
            # Método 2: Extracción con manejo de bloques
            text_blocks = page.get_text("blocks")
            text_from_blocks = "\n".join([block[4] for block in text_blocks])
            
            # Método 3: Extracción con diccionario
            text_dict = page.get_text("dict")
            text_from_dict = ""
            if "blocks" in text_dict:
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            if "spans" in line:
                                for span in line["spans"]:
                                    if "text" in span:
                                        text_from_dict += span["text"] + " "
            
            # Seleccionar el texto más limpio
            candidates = [
                text_standard,
                text_from_blocks,
                text_from_dict
            ]
            
            # Elegir el texto que parece más válido
            for candidate in candidates:
                # Verificar si el texto parece válido (no tiene caracteres extraños)
                if candidate and not re.search(r'[^\w\s\.,;:¿?¡!@#$%^&*()_+\-=\[\]{}|\\/<>""''–—]', candidate):
                    text = candidate
                    break
            
            if not text:  # Si ningún método funcionó bien, usar el estándar
                text = text_standard
            
            content['full_text'] += text
            
            # Identificar secciones (mejorado para manejar diferentes formatos)
            potential_sections = []
            
            # Buscar por patrones comunes de títulos
            patterns = [
                r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,50}(?:\n|$)',  # Mayúsculas al inicio
                r'^(?:[IVX]+\.?\s+)?[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ\s]{2,50}(?:\n|$)',  # Con números romanos
                r'^\d+\.?\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ\s]{2,50}(?:\n|$)'  # Con números
            ]
            
            for pattern in patterns:
                sections = re.findall(pattern, text, flags=re.MULTILINE)
                potential_sections.extend([s.strip() for s in sections])
            
            # Filtrar secciones duplicadas y limpiar
            cleaned_sections = []
            for section in potential_sections:
                # Limpiar caracteres no deseados
                cleaned = re.sub(r'[^\w\sÁÉÍÓÚÑáéíóúñ\.,;:]', '', section)
                cleaned = cleaned.strip()
                if cleaned and cleaned not in cleaned_sections:
                    cleaned_sections.append(cleaned)
            
            content['sections'].extend(cleaned_sections)

        # Analizar párrafos con mejor limpieza
        paragraphs = [p.strip() for p in content['full_text'].split('\n\n') if p.strip()]
        content['paragraphs'] = [p for p in paragraphs if len(p.split()) > 1]  # Ignorar párrafos de una sola palabra

        # Analizar palabras y términos con mejor limpieza
        words = []
        for word in re.findall(r'\w+', content['full_text'].lower()):
            # Limpiar la palabra
            word = re.sub(r'[^\w\sáéíóúñ]', '', word)
            if len(word) > 3 and not word.isdigit():
                words.append(word)
        
        content['word_frequencies'] = Counter(words)
        content['total_words'] = len(words)

        # Analizar términos de seguros
        text_lower = content['full_text'].lower()
        for term in self.insurance_terms:
            count = len(re.findall(r'\b' + term + r'\b', text_lower))
            if count > 0:
                content['insurance_terms_freq'][term] = count

        doc.close()
        return content

    def generate_metadata(self, pdf_path: str) -> Dict:
        """Genera metadatos enriquecidos para el documento PDF."""
        # Obtener estadísticas del archivo
        file_stats = os.stat(pdf_path)
        
        # Extraer y analizar contenido
        content = self.extract_text_content(pdf_path)
        
        # Generar hash único del documento
        with open(pdf_path, 'rb') as f:
            doc_hash = hashlib.md5(f.read()).hexdigest()

        # Identificar título del documento
        first_text = content['paragraphs'][0] if content['paragraphs'] else ''
        title_match = re.search(r'^[^\n]{10,100}', first_text)
        doc_title = title_match.group(0) if title_match else os.path.basename(pdf_path)

        # Construir metadatos
        metadata = {
            'file_info': {
                'filename': os.path.basename(pdf_path),
                'doc_hash': doc_hash,
                'file_size_bytes': file_stats.st_size,
                'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'created_date': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                'path': pdf_path
            },
            'document_info': {
                'title': doc_title,
                'num_pages': fitz.open(pdf_path).page_count,
                'word_count': content['total_words'],
                'paragraph_count': len(content['paragraphs'])
            },
            'content_summary': {
                'keywords': [word for word, _ in content['word_frequencies'].most_common(10)],
                'insurance_terms_present': list(content['insurance_terms_freq'].keys()),
                'insurance_terms_frequencies': dict(content['insurance_terms_freq']),
                'insurance_terms_ratio': sum(content['insurance_terms_freq'].values()) / content['total_words'] if content['total_words'] > 0 else 0,
                'main_sections': content['sections'][:10]
            },
            'extraction_info': {
                'extraction_date': datetime.now().isoformat(),
                'generator_version': '1.0',
                'insurance_terms_analyzed': self.insurance_terms
            }
        }

        return metadata

    def process_all_documents(self) -> Dict[str, Dict]:
        """Procesa todos los documentos PDF en el directorio."""
        all_metadata = {}
        
        print("🔍 Generando metadatos para los documentos...")
        for pdf_file in self.pdf_files:
            pdf_path = os.path.join(self.data_dir, pdf_file)
            print(f"\n📄 Procesando: {pdf_file}")
            
            try:
                metadata = self.generate_metadata(pdf_path)
                all_metadata[pdf_file] = metadata
                print(f"✅ Metadatos generados exitosamente")
                
            except Exception as e:
                print(f"❌ Error procesando {pdf_file}: {str(e)}")
                continue
        
        return all_metadata

    def save_metadata(self, metadata: Dict[str, Dict], output_file: str = "documentos_metadata.json"):
        """Guarda los metadatos en un archivo JSON."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Metadatos guardados en '{output_file}'")
        except Exception as e:
            print(f"❌ Error guardando metadatos: {str(e)}")

def main():
    generator = MetadataGenerator()
    
    if not generator.pdf_files:
        print("❌ No se encontraron archivos PDF en el directorio preparsed_data/")
        return
    
    # Procesar documentos y generar metadatos
    all_metadata = generator.process_all_documents()
    
    # Guardar metadatos
    generator.save_metadata(all_metadata)

if __name__ == "__main__":
    main() 