import streamlit as st
import numpy as np
import faiss
import os

def cargar_datos():
    """Carga los datos de la base vectorial."""
    try:
        ids = np.load('vector_ids.npy')
        texts = np.load('vector_texts.npy')
        index = faiss.read_index('vector_index.faiss')
        return ids, texts, index
    except Exception as e:
        st.error(f"❌ Error cargando los datos: {str(e)}")
        return None, None, None

def main():
    st.title("📚 Visor de Base de Datos Vectorial")
    
    # Cargar datos
    ids, texts, index = cargar_datos()
    if ids is None:
        st.error("No se pudieron cargar los datos. Verifica que existan los archivos vector_ids.npy, vector_texts.npy y vector_index.faiss")
        return
    
    st.write(f"Total de fragmentos en la base de datos: {len(ids)}")
    
    # Selector de modo de visualización
    modo = st.radio(
        "Selecciona modo de visualización:",
        ["Ver todos los fragmentos", "Buscar por similitud"]
    )
    
    if modo == "Ver todos los fragmentos":
        # Mostrar todos los fragmentos con paginación
        fragmentos_por_pagina = 25
        total_paginas = len(ids) // fragmentos_por_pagina + (1 if len(ids) % fragmentos_por_pagina > 0 else 0)
        
        pagina = st.number_input(
            "Página",
            min_value=1,
            max_value=total_paginas,
            value=1
        )
        
        inicio = (pagina - 1) * fragmentos_por_pagina
        fin = min(inicio + fragmentos_por_pagina, len(ids))
        
        for i in range(inicio, fin):
            with st.expander(f"📄 {ids[i]}"):
                st.write(texts[i])
                
        st.write(f"Página {pagina} de {total_paginas}")
        
    else:
        # Búsqueda por similitud
        from sentence_transformers import SentenceTransformer
        
        query = st.text_input("🔍 Ingresa tu búsqueda:")
        num_resultados = st.slider("Número de resultados", 1, 10, 3)
        
        if query and st.button("Buscar"):
            try:
                # Cargar modelo de embeddings
                model = SentenceTransformer("all-MiniLM-L6-v2")
                
                # Generar embedding de la consulta
                query_embedding = model.encode([query])[0]
                
                # Buscar documentos similares
                D, I = index.search(query_embedding.reshape(1, -1), num_resultados)
                
                # Mostrar resultados
                st.write("### 📊 Resultados más similares:")
                for i, (idx, dist) in enumerate(zip(I[0], D[0])):
                    with st.expander(f"🔍 Resultado {i+1} - {ids[idx]} (Distancia: {dist:.2f})"):
                        st.write(texts[idx])
                        
            except Exception as e:
                st.error(f"❌ Error en la búsqueda: {str(e)}")

if __name__ == "__main__":
    main() 