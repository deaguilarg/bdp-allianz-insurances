from ctransformers import AutoModelForCausalLM
import os

def test_modelo():
    # Verificar si existe el modelo
    modelo_path = "llama-2-7b-chat.q4_k_m.gguf"
    if not os.path.exists(modelo_path):
        print(f"❌ Error: No se encontró el modelo en {modelo_path}")
        return

    print("🔄 Cargando modelo...")
    try:
        # Cargar el modelo con configuración básica
        llm = AutoModelForCausalLM.from_pretrained(
            modelo_path,
            model_type="llama",
            gpu_layers=0,
            context_length=2048,
            threads=4
        )
        
        # Prompt de prueba simple
        prompt = """<s>[INST] <<SYS>>
        Eres un asistente útil que responde en español.
        <</SYS>>
        
        ¿Cuál es la capital de Francia? [/INST]"""

        print("\n🤖 Generando respuesta...")
        respuesta = llm(
            prompt,
            max_new_tokens=128,
            temperature=0.7,
            stop=["</s>", "[INST]"]
        )

        print("\n📝 Respuesta del modelo:")
        print(respuesta.split("[/INST]")[-1].strip())

    except Exception as e:
        print(f"❌ Error al usar el modelo: {str(e)}")

if __name__ == "__main__":
    test_modelo() 