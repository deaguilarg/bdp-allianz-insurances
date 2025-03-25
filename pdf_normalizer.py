import os
import fitz
import re
from typing import Dict, List, Optional
import json
from dataclasses import dataclass, asdict
import spacy
from tqdm import tqdm
import pandas as pd
from datetime import datetime

@dataclass
class SeguroInfo:
    nombre: str
    ramo: str
    coberturas: List[str]
    perfil: str
    archivo: str

class PDFNormalizer:
    def __init__(self, data_dir: str = "preparsed_data"):
        self.data_dir = data_dir
        # Cargar modelo de spaCy para español
        try:
            self.nlp = spacy.load("es_core_news_md")
        except:
            os.system("python -m spacy download es_core_news_md")
            self.nlp = spacy.load("es_core_news_md")
        
        # Patrones para identificar ramos de seguro
        self.ramos_patrones = {
            'auto': r'(?i)(automóvil|vehículo|coche|auto|conductor)',
            'moto': r'(?i)(motocicleta|moto|ciclomotor)',
            'viaje': r'(?i)(viaje|viajero|equipaje|asistencia.?viaje)',
            'hogar': r'(?i)(hogar|vivienda|casa|contenido|continente)',
            'vida': r'(?i)(vida|fallecimiento|supervivencia)',
            'salud': r'(?i)(salud|médico|hospitalización|dental)',
            'accidentes': r'(?i)(accidente.?personal|invalidez)',
            'responsabilidad_civil': r'(?i)(responsabilidad.?civil|rc)',
            'comercio': r'(?i)(negocio|comercio|empresa|pyme)',
            'comunidades': r'(?i)(comunidad.?propietarios|edificio)'
        }
        
        # Patrones para identificar coberturas
        self.cobertura_patrones = [
            r'(?i)cobertura[s]?\s*(?:incluida[s]?|contratada[s]?)?[:\n]',
            r'(?i)(?:el seguro|la póliza)\s+(?:cubre|incluye)[:\n]',
            r'(?i)garantías[:\n]',
            r'(?i)riesgos cubiertos[:\n]'
        ]
        
        # Patrones para identificar perfiles
        self.perfil_patrones = [
            r'(?i)dirigido a[:\n]',
            r'(?i)perfil del asegurado[:\n]',
            r'(?i)quién puede contratar[:\n]',
            r'(?i)este seguro es para[:\n]'
        ]

    def _extraer_texto_limpio(self, pdf_path: str) -> str:
        """Extrae y limpia el texto del PDF."""
        doc = fitz.open(pdf_path)
        texto = ""
        for page in doc:
            texto += page.get_text()
        doc.close()
        
        # Limpiar texto
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'[^\w\s.,;:¿?¡!@#$%^&*()_+\-=\[\]{}|\\/<>""''–—áéíóúñÁÉÍÓÚÑ]', '', texto)
        return texto

    def _identificar_nombre(self, texto: str) -> str:
        """Identifica el nombre del seguro."""
        # Patrones comunes para nombres de seguros
        patrones = [
            r'(?i)seguro\s+(?:de\s+)?([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)(?:\.|$|\n)',
            r'(?i)póliza\s+(?:de\s+)?([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)(?:\.|$|\n)',
            r'(?i)([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)\s+seguro(?:\s+|$|\n)'
        ]
        
        for patron in patrones:
            match = re.search(patron, texto[:500])  # Buscar en los primeros 500 caracteres
            if match:
                nombre = match.group(1).strip()
                if len(nombre) > 5:  # Evitar nombres muy cortos
                    return nombre
        
        return "Nombre no identificado"

    def _identificar_ramo(self, texto: str) -> str:
        """Identifica el ramo del seguro."""
        max_matches = 0
        ramo_identificado = "No identificado"
        
        for ramo, patron in self.ramos_patrones.items():
            matches = len(re.findall(patron, texto))
            if matches > max_matches:
                max_matches = matches
                ramo_identificado = ramo
        
        return ramo_identificado

    def _extraer_coberturas(self, texto: str) -> List[str]:
        """Extrae las coberturas del seguro."""
        coberturas = set()
        
        # Buscar sección de coberturas
        for patron in self.cobertura_patrones:
            match = re.search(patron + r'(.*?)(?:\n\n|\.$)', texto, re.DOTALL)
            if match:
                seccion = match.group(1)
                
                # Procesar con spaCy para identificar frases relevantes
                doc = self.nlp(seccion)
                
                # Identificar elementos de lista o frases que parezcan coberturas
                for sent in doc.sents:
                    # Limpiar y normalizar la frase
                    cobertura = sent.text.strip()
                    cobertura = re.sub(r'^\W+|\W+$', '', cobertura)
                    
                    # Filtrar coberturas válidas
                    if (len(cobertura.split()) >= 2 and  # Al menos dos palabras
                        len(cobertura.split()) <= 10 and  # No muy larga
                        not re.match(r'^\d+$', cobertura)):  # No solo números
                        coberturas.add(cobertura)
        
        return list(coberturas)

    def _identificar_perfil(self, texto: str) -> str:
        """Identifica el perfil objetivo del seguro."""
        for patron in self.perfil_patrones:
            match = re.search(patron + r'(.*?)(?:\n\n|\.$)', texto, re.DOTALL)
            if match:
                perfil = match.group(1).strip()
                # Limpiar y normalizar el perfil
                perfil = re.sub(r'\s+', ' ', perfil)
                if len(perfil) > 10:  # Evitar perfiles muy cortos
                    return perfil
        
        # Si no se encuentra un perfil explícito, intentar inferirlo
        doc = self.nlp(texto[:1000])  # Analizar el inicio del documento
        for sent in doc.sents:
            if any(palabra in sent.text.lower() for palabra in ['dirigido', 'destinado', 'para', 'cliente']):
                return sent.text.strip()
        
        return "Perfil no especificado"

    def normalizar_pdf(self, pdf_path: str) -> Optional[SeguroInfo]:
        """Procesa un PDF y extrae la información normalizada."""
        try:
            texto = self._extraer_texto_limpio(pdf_path)
            
            return SeguroInfo(
                nombre=self._identificar_nombre(texto),
                ramo=self._identificar_ramo(texto),
                coberturas=self._extraer_coberturas(texto),
                perfil=self._identificar_perfil(texto),
                archivo=os.path.basename(pdf_path)
            )
        except Exception as e:
            print(f"Error procesando {pdf_path}: {str(e)}")
            return None

    def procesar_directorio(self) -> List[Dict]:
        """Procesa todos los PDFs en el directorio y genera Excel."""
        resultados = []
        pdf_files = [f for f in os.listdir(self.data_dir) if f.endswith('.pdf')]
        
        print(f"🔍 Procesando {len(pdf_files)} archivos PDF...")
        for pdf_file in tqdm(pdf_files):
            pdf_path = os.path.join(self.data_dir, pdf_file)
            info = self.normalizar_pdf(pdf_path)
            if info:
                resultados.append(asdict(info))
        
        if not resultados:
            print("❌ No se encontraron resultados para procesar")
            return []

        # Guardar resultados en JSON
        with open('seguros_normalizados.json', 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        try:
            # Crear DataFrame
            df_seguros = pd.DataFrame(resultados)
            
            # Crear Excel con múltiples hojas
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = f'analisis_seguros_{timestamp}.xlsx'
            
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                # Configurar el libro de trabajo
                workbook = writer.book
                
                # Formato para títulos
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4F81BD',
                    'font_color': 'white',
                    'border': 1,
                    'align': 'center'
                })
                
                # Formato para contenido
                content_format = workbook.add_format({
                    'border': 1,
                    'align': 'left',
                    'valign': 'top',
                    'text_wrap': True
                })
                
                # 1. Hoja principal con resumen
                df_resumen = df_seguros[['archivo', 'nombre', 'ramo', 'perfil']]
                df_resumen = df_resumen.sort_values('ramo')
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Ajustar formato de la hoja de resumen
                worksheet = writer.sheets['Resumen']
                for col_num, value in enumerate(df_resumen.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('A:A', 30)  # Archivo
                worksheet.set_column('B:B', 40)  # Nombre
                worksheet.set_column('C:C', 20)  # Ramo
                worksheet.set_column('D:D', 50)  # Perfil
                
                # 2. Hoja de coberturas
                coberturas_data = []
                for resultado in resultados:
                    nombre_archivo = resultado['archivo']
                    ramo = resultado['ramo']
                    for cobertura in resultado['coberturas']:
                        coberturas_data.append({
                            'Archivo': nombre_archivo,
                            'Ramo': ramo,
                            'Cobertura': cobertura
                        })
                
                if coberturas_data:
                    df_coberturas = pd.DataFrame(coberturas_data)
                    df_coberturas = df_coberturas.sort_values(['Ramo', 'Archivo'])
                    df_coberturas.to_excel(writer, sheet_name='Coberturas', index=False)
                    
                    # Ajustar formato de la hoja de coberturas
                    worksheet = writer.sheets['Coberturas']
                    for col_num, value in enumerate(df_coberturas.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column('A:A', 30)  # Archivo
                    worksheet.set_column('B:B', 20)  # Ramo
                    worksheet.set_column('C:C', 60)  # Cobertura
                
                # 3. Hoja de estadísticas
                stats_data = {
                    'Ramo': [],
                    'Cantidad': [],
                    'Promedio_Coberturas': []
                }
                
                for ramo in df_seguros['ramo'].unique():
                    docs_ramo = df_seguros[df_seguros['ramo'] == ramo]
                    stats_data['Ramo'].append(ramo)
                    stats_data['Cantidad'].append(len(docs_ramo))
                    stats_data['Promedio_Coberturas'].append(
                        sum(len(c) for c in docs_ramo['coberturas']) / len(docs_ramo)
                    )
                
                df_stats = pd.DataFrame(stats_data)
                df_stats = df_stats.sort_values('Cantidad', ascending=False)
                df_stats.to_excel(writer, sheet_name='Estadísticas', index=False)
                
                # Ajustar formato de la hoja de estadísticas
                worksheet = writer.sheets['Estadísticas']
                for col_num, value in enumerate(df_stats.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('A:A', 20)  # Ramo
                worksheet.set_column('B:B', 15)  # Cantidad
                worksheet.set_column('C:C', 25)  # Promedio_Coberturas
            
            print(f"✅ Resultados guardados en '{excel_path}'")
        except Exception as e:
            print(f"❌ Error generando el Excel: {str(e)}")
            print("Los resultados están disponibles en 'seguros_normalizados.json'")
        
        return resultados

def main():
    normalizer = PDFNormalizer()
    resultados = normalizer.procesar_directorio()
    
    # Mostrar resumen en consola
    print("\n📊 Resumen de procesamiento:")
    print(f"Total de documentos procesados: {len(resultados)}")
    
    # Mostrar distribución de ramos
    ramos = {}
    for r in resultados:
        ramo = r['ramo']
        ramos[ramo] = ramos.get(ramo, 0) + 1
    
    print("\nDistribución por ramo:")
    for ramo, count in sorted(ramos.items(), key=lambda x: x[1], reverse=True):
        print(f"- {ramo}: {count}")

if __name__ == "__main__":
    main() 