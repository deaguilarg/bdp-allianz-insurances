from huggingface_hub import hf_hub_download

def download_model():
    print("Iniciando descarga del modelo...")
    try:
        # Descargar el modelo
        model_path = hf_hub_download(
            repo_id="TheBloke/Llama-2-7b-Chat-GGUF",
            filename="llama-2-7b-chat.Q5_K_S.gguf",
            local_dir=".",
            local_dir_use_symlinks=False
        )
        print(f"✅ Modelo descargado exitosamente en: {model_path}")
    except Exception as e:
        print(f"❌ Error al descargar el modelo: {str(e)}")

if __name__ == "__main__":
    download_model()