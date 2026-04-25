import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def call_ollama(prompt: str, model: str = "llama3") -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=240)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ **Cannot reach Ollama.** "
            "Run `ollama serve` and ensure your model is pulled "
            "(e.g. `ollama pull llama3`)."
        )
    except requests.exceptions.Timeout:
        return "⚠️ **Request timed out.** Try a smaller log snippet or a faster model."
    except Exception as e:
        return f"⚠️ **Ollama error:** {e}"
