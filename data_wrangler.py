import os
import fitz  # PyMuPDF
import pandas as pd
from tqdm import tqdm
import re
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from datetime import datetime

class PDFAnalyzer:
    def __init__(self, data_dir="preparsed_data"):
        self.data_dir = data_dir
        self.pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        self.insurance_terms = [
            'póliza', 'prima', 'deducible', 'cobertura', 'exclusiones', 
            'beneficiario', 'asegurado', 'aseguradora', 'siniestro', 
            'indemnización', 'reclamación', 'vigencia', 'renovación', 
            'antigüedad', 'cargas', 'franquicia', 'cláusulas'
        ]
        
    def analyze_pdf_structure(self, pdf_path):
        """Analiza la estructura de un PDF y retorna estadísticas."""
        doc = fitz.open(pdf_path)
        stats = {
            'num_pages': len(doc),
            'chars_per_page': [],
            'words_per_page': [],
            'fonts': set(),
            'text_blocks': [],
            'images': 0
        }
        
        for page in doc:
            text = page.get_text()
            words = text.split()
            stats['chars_per_page'].append(len(text))
            stats['words_per_page'].append(len(words))
            
            # Analizar fuentes
            for block in page.get_text("dict")["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            stats['fonts'].add(span['font'])
            
            # Contar bloques de texto
            stats['text_blocks'].append(len(page.get_text_blocks()))
            
            # Contar imágenes
            stats['images'] += len(page.get_images())
        
        return stats
    
    def test_chunk_sizes(self, pdf_path, chunk_sizes=[256, 512, 1024]):
        """Prueba diferentes tamaños de chunk y analiza resultados."""
        doc = fitz.open(pdf_path)
        results = []
        
        for size in chunk_sizes:
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Dividir en chunks
            words = text.split()
            chunks = [' '.join(words[i:i + size]) for i in range(0, len(words), size)]
            
            # Analizar chunks
            chunk_stats = {
                'chunk_size': size,
                'num_chunks': len(chunks),
                'avg_chunk_length': np.mean([len(chunk) for chunk in chunks]),
                'complete_sentences': sum(1 for chunk in chunks if chunk.strip().endswith('.')),
                'broken_sentences': sum(1 for chunk in chunks if not chunk.strip().endswith('.'))
            }
            results.append(chunk_stats)
        
        return pd.DataFrame(results)
    
    def analyze_text_patterns(self, pdf_path):
        """Analiza patrones en el texto como secciones, títulos, etc."""
        doc = fitz.open(pdf_path)
        patterns = {
            'uppercase_lines': [],
            'bullet_points': 0,
            'numbered_lists': 0,
            'potential_tables': 0,
            'section_markers': [],
            'special_sections': []
        }
        
        for page in doc:
            text = page.get_text()
            lines = text.split('\n')
            
            # Detectar líneas en mayúsculas (posibles títulos)
            patterns['uppercase_lines'].extend([
                line.strip() for line in lines 
                if line.isupper() and len(line.strip()) > 10
            ])
            
            # Detectar viñetas y listas numeradas
            patterns['bullet_points'] += len(re.findall(r'[•·●○◦-]', text))
            patterns['numbered_lists'] += len(re.findall(r'^\d+[\.\)]', text, re.MULTILINE))
            
            # Detectar posibles tablas (basado en patrones comunes de tablas)
            table_indicators = [
                len(re.findall(r'\|\s+\|', text)),  # Columnas separadas por |
                len(re.findall(r'\t', text)),       # Tabulaciones
                len([l for l in lines if l.count('  ') > 3])  # Múltiples espacios
            ]
            patterns['potential_tables'] += sum(1 for i in table_indicators if i > 0)
            
            # Detectar marcadores de sección
            section_matches = re.findall(r'(?i)(capítulo|sección|artículo)\s+[\dIVXLCM]+', text)
            patterns['section_markers'].extend(section_matches)
            
            # Detectar secciones especiales
            special_sections = re.findall(r'(?i)(exclusiones|coberturas|definiciones|garantías|condiciones)', text)
            patterns['special_sections'].extend(special_sections)
        
        # Limpiar y deduplicar resultados
        patterns['uppercase_lines'] = list(set(patterns['uppercase_lines']))
        patterns['section_markers'] = list(set(patterns['section_markers']))
        patterns['special_sections'] = list(set(patterns['special_sections']))
        
        return patterns

    def analyze_content_structure(self, pdf_path):
        """Analiza la estructura de contenido del documento."""
        doc = fitz.open(pdf_path)
        structure = {
            'paragraphs': [],
            'avg_paragraph_length': 0,
            'sentence_lengths': [],
            'word_frequencies': Counter(),
            'insurance_terms_freq': Counter(),
            'total_words': 0
        }
        
        text = ""
        for page in doc:
            text += page.get_text()
        
        # Analizar párrafos
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        structure['paragraphs'] = len(paragraphs)
        structure['avg_paragraph_length'] = np.mean([len(p.split()) for p in paragraphs])
        
        # Analizar oraciones
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        structure['sentence_lengths'] = [len(s.split()) for s in sentences]
        
        # Frecuencia de palabras (excluyendo palabras de 3 o menos letras)
        words = [w.lower() for w in re.findall(r'\w+', text.lower()) if len(w) > 3]
        structure['word_frequencies'] = Counter(words)
        structure['total_words'] = len(words)
        
        # Frecuencia de términos de seguros
        text_lower = text.lower()
        for term in self.insurance_terms:
            count = len(re.findall(r'\b' + term + r'\b', text_lower))
            if count > 0:
                structure['insurance_terms_freq'][term] = count
        
        # Calcular ratio de términos de seguros
        total_insurance_terms = sum(structure['insurance_terms_freq'].values())
        structure['insurance_terms_ratio'] = total_insurance_terms / structure['total_words'] if structure['total_words'] > 0 else 0
        
        return structure

    def visualize_document_structure(self, pdf_path):
        """Visualiza la estructura del documento."""
        stats = self.analyze_pdf_structure(pdf_path)
        content_stats = self.analyze_content_structure(pdf_path)
        
        # Crear visualizaciones
        fig = plt.figure(figsize=(15, 15))
        
        # Título del documento y estadísticas básicas
        plt.suptitle(f"Análisis de: {os.path.basename(pdf_path)}\nPáginas: {stats['num_pages']}", 
                    fontsize=14, y=0.95)
        
        # Definir subplots
        gs = plt.GridSpec(3, 2, figure=fig)
        ax1 = fig.add_subplot(gs[0, :])  # Palabras por página (ocupa todo el ancho)
        ax2 = fig.add_subplot(gs[1, 0])  # Distribución de longitud de oraciones
        ax3 = fig.add_subplot(gs[1, 1])  # Top 10 palabras más frecuentes
        ax4 = fig.add_subplot(gs[2, :])  # Términos de seguros (ocupa todo el ancho)
        
        # Palabras por página
        ax1.plot(stats['words_per_page'])
        ax1.set_title('Palabras por Página')
        ax1.set_xlabel('Número de Página')
        ax1.set_ylabel('Palabras')
        
        # Distribución de longitud de oraciones
        if content_stats['sentence_lengths']:
            ax2.hist(content_stats['sentence_lengths'], bins=20)
            ax2.set_title('Distribución de Longitud de Oraciones')
            ax2.set_xlabel('Palabras por Oración')
            ax2.set_ylabel('Frecuencia')
        
        # Top 10 palabras más frecuentes (excluyendo palabras cortas)
        top_words = content_stats['word_frequencies'].most_common(10)
        if top_words:
            words, counts = zip(*top_words)
            ax3.barh(words, counts)
            ax3.set_title('Top 10 Palabras más Frecuentes\n(>3 letras)')
            ax3.set_xlabel('Frecuencia')
        
        # Términos de seguros y su frecuencia
        terms = list(content_stats['insurance_terms_freq'].keys())
        freqs = list(content_stats['insurance_terms_freq'].values())
        if terms:
            ax4.bar(terms, freqs)
            ax4.set_title(f'Frecuencia de Términos de Seguros\nRatio: {content_stats["insurance_terms_ratio"]}')
            ax4.set_xticklabels(terms, rotation=45, ha='right')
            ax4.set_ylabel('Frecuencia')
        
        plt.tight_layout()
        return plt

    def export_to_excel(self, all_stats, output_file="analisis_pdfs.xlsx"):
        """Exporta todos los datos del análisis a un archivo Excel para Power BI."""
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Hoja 1: Información general de documentos
            docs_info = []
            for doc_name, stats in all_stats.items():
                doc_info = {
                    'Documento': doc_name,
                    'Fecha_Análisis': datetime.now().strftime('%Y-%m-%d'),
                    'Número_Páginas': stats['structure']['num_pages'],
                    'Total_Imágenes': stats['structure']['images'],
                    'Promedio_Palabras_Por_Página': np.mean(stats['structure']['words_per_page']),
                    'Total_Párrafos': stats['content']['paragraphs'],
                    'Promedio_Palabras_Por_Párrafo': stats['content']['avg_paragraph_length'],
                    'Ratio_Términos_Seguros': stats['content']['insurance_terms_ratio']
                }
                docs_info.append(doc_info)
            
            df_docs = pd.DataFrame(docs_info)
            df_docs.to_excel(writer, sheet_name='Información_General', index=False)

            # Hoja 2: Palabras por página
            words_per_page = []
            for doc_name, stats in all_stats.items():
                for page_num, word_count in enumerate(stats['structure']['words_per_page'], 1):
                    words_per_page.append({
                        'Documento': doc_name,
                        'Número_Página': page_num,
                        'Cantidad_Palabras': word_count
                    })
            
            df_words = pd.DataFrame(words_per_page)
            df_words.to_excel(writer, sheet_name='Palabras_Por_Página', index=False)

            # Hoja 3: Términos de seguros
            insurance_terms = []
            for doc_name, stats in all_stats.items():
                for term, freq in stats['content']['insurance_terms_freq'].items():
                    insurance_terms.append({
                        'Documento': doc_name,
                        'Término': term,
                        'Frecuencia': freq
                    })
            
            df_terms = pd.DataFrame(insurance_terms)
            df_terms.to_excel(writer, sheet_name='Términos_Seguros', index=False)

            # Hoja 4: Palabras más frecuentes
            frequent_words = []
            for doc_name, stats in all_stats.items():
                for word, count in stats['content']['word_frequencies'].most_common(50):  # Top 50
                    frequent_words.append({
                        'Documento': doc_name,
                        'Palabra': word,
                        'Frecuencia': count
                    })
            
            df_words_freq = pd.DataFrame(frequent_words)
            df_words_freq.to_excel(writer, sheet_name='Palabras_Frecuentes', index=False)

            # Hoja 5: Longitud de oraciones
            sentence_lengths = []
            for doc_name, stats in all_stats.items():
                for length in stats['content']['sentence_lengths']:
                    sentence_lengths.append({
                        'Documento': doc_name,
                        'Longitud_Oración': length
                    })
            
            df_sentences = pd.DataFrame(sentence_lengths)
            df_sentences.to_excel(writer, sheet_name='Longitud_Oraciones', index=False)

def main():
    analyzer = PDFAnalyzer()
    
    if not analyzer.pdf_files:
        print("❌ No se encontraron archivos PDF en el directorio preparsed_data/")
        return
    
    print("🔍 Analizando PDFs...")
    all_stats = {}
    
    for pdf_file in analyzer.pdf_files:
        pdf_path = os.path.join(analyzer.data_dir, pdf_file)
        print(f"\n📄 Analizando: {pdf_file}")
        
        try:
            # Recopilar todas las estadísticas
            structure_stats = analyzer.analyze_pdf_structure(pdf_path)
            content_stats = analyzer.analyze_content_structure(pdf_path)
            
            all_stats[pdf_file] = {
                'structure': structure_stats,
                'content': content_stats
            }
            
            # Mostrar resumen en consola
            print("\n📊 Estadísticas básicas:")
            print(f"- Páginas: {structure_stats['num_pages']}")
            print(f"- Promedio de palabras por página: {np.mean(structure_stats['words_per_page']):.0f}")
            print(f"- Imágenes totales: {structure_stats['images']}")
            
            print("\n📝 Análisis de contenido:")
            print(f"- Número de párrafos: {content_stats['paragraphs']}")
            print(f"- Promedio de palabras por párrafo: {content_stats['avg_paragraph_length']:.1f}")
            print(f"\n📊 Análisis de términos de seguros:")
            print(f"- Ratio de términos de seguros: {content_stats['insurance_terms_ratio']:.4f}")
            
            # Generar visualización
            plt = analyzer.visualize_document_structure(pdf_path)
            plt.savefig(f"analysis_{pdf_file}.png", bbox_inches='tight', dpi=300)
            plt.close()
            
        except Exception as e:
            print(f"❌ Error analizando {pdf_file}: {str(e)}")
            continue
    
    # Exportar todos los datos a Excel
    try:
        analyzer.export_to_excel(all_stats)
        print("\n✅ Datos exportados a 'analisis_pdfs.xlsx'")
        print("   Este archivo puede ser importado directamente en Power BI")
    except Exception as e:
        print(f"❌ Error exportando a Excel: {str(e)}")

if __name__ == "__main__":
    main() 