import requests

def query_llm(prompt: str, model: str = "mistral") -> str:
    """
    Consulta uma LLM local via Ollama com prompt fornecido.
    Requer Ollama rodando localmente.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=180  # aumentado para evitar timeout com textos longos
        )
        response.raise_for_status()
        data = response.json()
        result = data.get("response", "").strip()

        # Se a resposta for vazia, retorna texto original sem erro
        if not result:
            return "[ERRO] Resposta vazia da LLM. Texto original mantido."

        return result

    except requests.exceptions.Timeout:
        return "[ERRO DE CONEXÃO COM OLLAMA] Tempo limite excedido. Texto original mantido."

    except requests.exceptions.RequestException as e:
        return f"[ERRO DE CONEXÃO COM OLLAMA] {str(e)}"

    except requests.exceptions.JSONDecodeError as e:
        return f"[ERRO AO DECODIFICAR RESPOSTA JSON] {str(e)}"

    except Exception as e:
        return f"[ERRO INESPERADO NA LLM] {str(e)}"

def is_ollama_running() -> bool:
    try:
        test = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": "Diga apenas 'ativo'.",
                "stream": False
            },
            timeout=10
        )
        return test.status_code == 200 and "ativo" in test.text.lower()
    except:
        return False
    # Se não conseguir conectar, assume que o Ollama não está rodando
    # ou não está acessível.
    # Retorna False para indicar que o Ollama não está disponível.
    # Isso evita que o código que depende do Ollama falhe.
    # Em vez disso, ele pode continuar a execução sem a validação semântica.
    # Isso é útil para garantir que o aplicativo funcione mesmo sem o Ollama.
    # Se o Ollama estiver rodando, retorna True.
    # Isso indica que o Ollama está acessível e pode ser usado para validação semântica.
    # Isso permite que o código que depende do Ollama funcione corretamente.    
