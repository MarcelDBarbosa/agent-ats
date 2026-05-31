import os
from ollama import Client
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def get_ollama_client() -> Client:
    """
    Retorna uma instância configurada do cliente Ollama apontando para o Ollama Cloud.
    Valida a presença da OLLAMA_API_KEY.
    """
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key or api_key == "sua_chave_de_api_ollama_aqui":
        raise ValueError("OLLAMA_API_KEY não encontrada ou não configurada no arquivo .env")

    # Retorna o cliente oficial do Ollama passando a API key nos cabeçalhos
    return Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )
