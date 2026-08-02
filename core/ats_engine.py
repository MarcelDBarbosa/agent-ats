import asyncio
import json
import os

from ollama import Client


def load_system_prompt() -> str:
    """
    Carrega o prompt de sistema a partir de prompts/ats_system.txt de forma robusta e dinâmica.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.normpath(
        os.path.join(current_dir, "..", "prompts", "ats_system.txt")
    )

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(
            f"Arquivo de prompt do sistema não encontrado em: {prompt_path}"
        )

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


async def analyze_resume(client: Client, job_desc: str, resume_text: str) -> dict:
    """
    Envia a descrição da vaga e o currículo ao Ollama Cloud assincronamente via asyncio.to_thread.
    Exige retorno formatado em JSON.
    """
    system_prompt = load_system_prompt()

    # Envelopa a chamada síncrona do ollama.Client em um thread assíncrono para evitar bloquear o loop do FastAPI
    response = await asyncio.to_thread(
        client.chat,
        model="minimax-m2.7:cloud",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"VAGA:\n{job_desc}\n\nCURRÍCULO:\n{resume_text}",
            },
        ],
        format="json",
    )

    # Extrai o conteúdo do chat e faz o parsing para dicionário
    try:
        content = response.message.content
        if not content:
            raise ValueError("O Ollama Cloud retornou uma resposta vazia.")

        data = json.loads(content)
        return data
    except Exception as e:
        raise ValueError(f"O modelo não retornou um JSON válido: {str(e)}")
