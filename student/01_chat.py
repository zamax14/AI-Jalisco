"""Etapa 1. Solo habla: un chatbot SIN herramientas.

Pregúntale por el reciclaje de Tonalá: no tiene forma de consultar los datos.
"""
import os

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
cliente = OpenAI(base_url=os.environ["TALLER_BASE_URL"].rstrip("/") + "/llm/v1", api_key=os.environ["TALLER_TOKEN"])
MODELO = os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct")

mensajes = [{"role": "system", "content": (
    "Eres un asistente breve que responde en español. NO tienes acceso a bases de datos ni a internet. "
    "Si te piden cifras o indicadores concretos, di claramente que no puedes consultarlos y no inventes números."
)}]

print("=" * 70)
print("  Chat sin herramientas")
print("  Escribe 'salir' para terminar.")
print("=" * 70)

while (pregunta := input("\nTú: ").strip()).lower() != "salir":
    if not pregunta:
        continue
    mensajes.append({"role": "user", "content": pregunta})
    try:
        respuesta = cliente.chat.completions.create(model=MODELO, messages=mensajes, temperature=0.2)
    except openai.APIConnectionError:
        mensajes.pop()
        print("\n  No se pudo conectar al servidor. Revisa TALLER_BASE_URL en .env y tu conexión a Internet.")
        continue
    except openai.APIStatusError as e:
        mensajes.pop()
        print(f"\n  Error del servidor ({e.status_code}): {e.message}")
        continue
    texto = respuesta.choices[0].message.content
    mensajes.append({"role": "assistant", "content": texto})
    print("\nModelo:\n")
    print("    " + texto.replace("\n", "\n    "))
    print("\n" + "-" * 70)
