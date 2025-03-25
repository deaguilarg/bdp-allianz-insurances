import pandas as pd
from fpdf import FPDF
import os

# Cargar el archivo "seguros.xlsx"
file_path = os.path.join("preparsed_data", "seguros.xlsx")

# Cargar todas las hojas actualizadas
df_coberturas = pd.read_excel(file_path, sheet_name="Coberturas")
df_no_coberturas = pd.read_excel(file_path, sheet_name="No coberturas")
df_restricciones = pd.read_excel(file_path, sheet_name="Restricciones")
df_sumas = pd.read_excel(file_path, sheet_name="Sumas Aseguradas")
df_lugares = pd.read_excel(file_path, sheet_name="Lugares cobertura")
df_obligaciones = pd.read_excel(file_path, sheet_name="Obligaciones")

# Verificar nombres de columnas para asegurar consistencia
columnas_por_hoja = {
    "Coberturas": df_coberturas.columns.tolist(),
    "No coberturas": df_no_coberturas.columns.tolist(),
    "Restricciones": df_restricciones.columns.tolist(),
    "Sumas Aseguradas": df_sumas.columns.tolist(),
    "Lugares cobertura": df_lugares.columns.tolist(),
    "Obligaciones": df_obligaciones.columns.tolist()
}

# Función para agregar contenido agrupado por nombreSeguro
def agregar_info(seguros, df, campo, columna_valor):
    for seguro, grupo in df.groupby("nombreSeguro"):
        texto = "; ".join(grupo[columna_valor].dropna().astype(str).unique())
        if seguro not in seguros:
            seguros[seguro] = {}
        seguros[seguro][campo] = texto

# Preparar estructura
seguros = {}

# Agregar la información de cada hoja
agregar_info(seguros, df_coberturas, "Coberturas", "Cobertura")
agregar_info(seguros, df_no_coberturas, "No_coberturas", "No Cubre")
agregar_info(seguros, df_restricciones, "Restricciones", "Restricciones")
agregar_info(seguros, df_sumas, "Sumas_aseguradas", "Sumas Aseguradas")
agregar_info(seguros, df_lugares, "Lugares_cobertura", "Donde Estoy Cubierto")
agregar_info(seguros, df_obligaciones, "Obligaciones", "Obligaciones")

# Construir los chunks finales
chunks = []
for nombre, info in seguros.items():
    chunk = f"El seguro '{nombre}' de Allianz incluye:\n"
    if "Coberturas" in info:
        chunk += f"- Coberturas: {info['Coberturas']}\n"
    if "No_coberturas" in info:
        chunk += f"- Exclusiones: {info['No_coberturas']}\n"
    if "Restricciones" in info:
        chunk += f"- Restricciones: {info['Restricciones']}\n"
    if "Sumas_aseguradas" in info:
        chunk += f"- Sumas aseguradas: {info['Sumas_aseguradas']}\n"
    if "Lugares_cobertura" in info:
        chunk += f"- Lugares donde aplica la cobertura: {info['Lugares_cobertura']}\n"
    if "Obligaciones" in info:
        chunk += f"- Obligaciones del asegurado: {info['Obligaciones']}\n"
    chunks.append({"nombre": nombre, "texto": chunk})

# Generar PDF con los chunks
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

for chunk in chunks:
    pdf.multi_cell(0, 10, chunk['texto'])
    pdf.cell(0, 10, '', ln=True)  # Espacio entre chunks

# Guardar el PDF
pdf_output_path = os.path.join("preparsed_data", "seguros_chunks.pdf")
pdf.output(pdf_output_path)

print(f"✅ PDF generado: {pdf_output_path}")