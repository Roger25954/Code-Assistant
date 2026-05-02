# agent.py
import os
import re
from groq import Groq
from google import genai
from dotenv import load_dotenv
import logging

load_dotenv()

log = logging.getLogger(__name__)

# ─── Inicializar clientes ─────────────────────────────────────
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ─── Utilidad — limpiar respuestas de modelos de razonamiento ─
def _limpiar_respuesta(texto: str) -> str:
    """Elimina el bloque <think>...</think> que genera qwen3."""
    texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL)
    texto = re.sub(r'```python\n?', '', texto)
    texto = re.sub(r'```\n?', '', texto)
    return texto.strip()


# ─── Router — qué modelo hace qué tarea ──────────────────────
def get_completion(code: str, prefix: str) -> str:
    """
    Autocompletado inline — usa Groq + Qwen porque es ultra rápido.
    prefix = lo que el usuario escribió hasta ahora
    code   = todo el archivo para contexto
    """
    log.info("Pidiendo completion a Groq...")

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente de código. "
                    "El usuario está escribiendo código Python. "
                    "Completa SOLO la línea actual, sin explicaciones, "
                    "sin markdown, sin comentarios. Solo el código."
                )
            },
            {
                "role": "user",
                "content": f"Archivo completo:\n{code}\n\nCompleta esto: {prefix}"
            }
        ],
        max_tokens=150,  # completions cortas y rápidas
        temperature=0.1  # poca creatividad — queremos código preciso
    )

    return _limpiar_respuesta(response.choices[0].message.content)


def get_explanation(code: str) -> str:
    """
    Explicar código — usa Gemini porque razona mejor en lenguaje natural
    y puede manejar archivos largos con su contexto de 1M tokens.
    """
    log.info("Pidiendo explicación a Gemini...")

    response = gemini_client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Explica este código de forma clara y concisa en español:\n\n{code}"
    )

    return response.text


def get_fix(code: str, error: str) -> str:
    """
    Fix de bugs — usa Groq + Qwen porque está especializado en código.
    """
    log.info("Pidiendo fix a Groq...")

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un experto en debugging. "
                    "Analiza el error y retorna SOLO el código corregido, "
                    "sin explicaciones ni markdown."
                )
            },
            {
                "role": "user",
                "content": f"Código:\n{code}\n\nError:\n{error}"
            }
        ],
        max_tokens=500,
        temperature=0.1
    )

    return _limpiar_respuesta(response.choices[0].message.content)


def get_tests(code: str) -> str:
    """
    Generar tests — usa Groq + Qwen especializado en código.
    """
    log.info("Generando tests con Groq...")

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un experto en testing de Python. "
                    "Genera tests usando pytest. "
                    "IMPORTANTE: incluye siempre el import de las funciones que testeas. "
                    "Retorna SOLO el código de los tests, sin explicaciones ni markdown."
                )
            },
            {
                "role": "user",
                "content": f"Genera tests para este código:\n\n{code}"
            }
        ],
        max_tokens=800,
        temperature=0.1
    )

    return _limpiar_respuesta(response.choices[0].message.content)