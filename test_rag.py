from RAG import RAGSimple
import time

def test_rag():
    # Inicializar en modo prueba
    rag = RAGSimple(modo_prueba=True)
    
    # Preguntas de prueba
    preguntas_test = [
        "¿Qué cubre el seguro de moto?",
        "¿Cuál es el costo del seguro de comunidad?",
        "¿Qué documentos necesito para asegurar mi moto?"
    ]
    
    # Ejecutar pruebas
    tiempos = []
    for pregunta in preguntas_test:
        print(f"\n🔄 Probando: {pregunta}")
        inicio = time.time()
        respuesta = rag.generar_respuesta(pregunta)
        tiempo = time.time() - inicio
        tiempos.append(tiempo)
        print(f"⏱️ Tiempo: {tiempo:.2f}s")
        print(f"📝 Respuesta: {respuesta[:100]}...")
    
    # Mostrar estadísticas
    print("\n📊 Estadísticas:")
    print(f"Tiempo promedio: {sum(tiempos)/len(tiempos):.2f}s")
    print(f"Tiempo mínimo: {min(tiempos):.2f}s")
    print(f"Tiempo máximo: {max(tiempos):.2f}s")

if __name__ == "__main__":
    test_rag() 