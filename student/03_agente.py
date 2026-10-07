"""Etapa 3. El modelo elige y el programa ejecuta: un agente con tool calling.

El ciclo del agente:
  1. Mandamos la pregunta y la lista de herramientas (TOOLS) al modelo.
  2. Si el modelo pide herramientas (tool_calls), NOSOTROS las ejecutamos.
  3. Le devolvemos los resultados (role="tool") y repetimos.
  4. Cuando contesta con texto, esa es la respuesta final.
"""
import json
import os

import openai
from dotenv import load_dotenv
from openai import OpenAI

from tools import TOOLS, ejecutar

load_dotenv()
cliente = OpenAI(base_url=os.environ["TALLER_BASE_URL"].rstrip("/") + "/llm/v1",
                 api_key=os.environ["TALLER_TOKEN"], timeout=100, max_retries=1)
MODELO = os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct")
MAX_CICLOS = 10  # evita bucles infinitos
LINEAS_RESULTADO = 30  # cuántas líneas del resultado se muestran en pantalla

SISTEMA = (
    "Eres un analista que responde en español, breve y preciso. Tienes herramientas para consultar "
    "indicadores SIMULADOS de 2025 de 9 municipios del Área Metropolitana de Guadalajara (no son datos oficiales). "
    "Usa las herramientas para cualquier cifra; nunca inventes números. Incluye las unidades. "
    "Si la herramienta devuelve un error o no hay datos (por ejemplo pronósticos), dilo con claridad."
)


def mostrar_json(dato) -> None:
    """Imprime un JSON con sangría, recortado para que quepa en pantalla."""
    lineas = json.dumps(dato, ensure_ascii=False, indent=2).splitlines()
    for linea in lineas[:LINEAS_RESULTADO]:
        print("        " + linea)
    if len(lineas) > LINEAS_RESULTADO:
        print(f"        ... ({len(lineas) - LINEAS_RESULTADO} líneas más)")


def responder(mensajes: list) -> str:
    paso = 0
    for _ in range(MAX_CICLOS):
        r = cliente.chat.completions.create(model=MODELO, messages=mensajes, tools=TOOLS, temperature=0.1)
        msg = r.choices[0].message
        mensajes.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:  # el modelo ya contestó con texto
            return msg.content

        for llamada in msg.tool_calls:  # puede pedir varias herramientas a la vez
            paso += 1
            print(f"\n  [Paso {paso}] Modelo eligió: {llamada.function.name}")
            print(f"      Argumentos: {llamada.function.arguments}")
            resultado = ejecutar(llamada.function.name, llamada.function.arguments)
            print("      Resultado:")
            mostrar_json(resultado.get("data", resultado))
            mensajes.append({"role": "tool", "tool_call_id": llamada.id,
                             "content": json.dumps(resultado, ensure_ascii=False)})
    return "No pude terminar en pocos pasos; intenta una pregunta más concreta."


mensajes = [{"role": "system", "content": SISTEMA}]
print("=" * 70)
print("  Agente de indicadores AMG (datos simulados)")
print("  Escribe 'salir' para terminar.")
print("=" * 70)

while (pregunta := input("\nTú: ").strip()).lower() != "salir":
    if not pregunta:
        continue
    mensajes.append({"role": "user", "content": pregunta})
    try:
        respuesta = responder(mensajes)
        print("\n  Respuesta final:\n")
        print("    " + respuesta.replace("\n", "\n    "))
    except openai.RateLimitError:
        print("\n  El servidor está ocupado (429). Espera unos segundos y vuelve a intentar.")
    except (openai.APITimeoutError, openai.APIConnectionError):
        print("\n  No hubo respuesta del servidor (timeout o red). Revisa TALLER_BASE_URL e intenta de nuevo.")
    except openai.APIStatusError as e:
        print(f"\n  Error del servidor ({e.status_code}): {e.message}")
    print("\n" + "-" * 70)
