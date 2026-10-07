"""Herramientas del agente: funciones Python que llaman a la API REST de indicadores.

El modelo NUNCA elige una URL: solo puede pedir una de estas 5 funciones por su nombre.
"""
import json
import os
from urllib.parse import unquote

import httpx
from dotenv import load_dotenv

load_dotenv()
API = os.environ["TALLER_BASE_URL"].rstrip("/") + "/api/v1"


def _get(ruta: str, **params) -> dict:
    params = {k: v for k, v in params.items() if v is not None}
    r = httpx.get(API + ruta, params=params, timeout=15)
    print(f"      GET: {unquote(str(r.url))}  (HTTP {r.status_code})")
    if r.status_code >= 400:
        return {"error": r.json().get("detail", r.text)}  # el modelo verá el error, no cifras inventadas
    return r.json()


def listar_municipios():
    return _get("/municipios")


def listar_indicadores():
    return _get("/indicadores")


def consultar_indicadores(municipio: str, ids: list[str] | None = None):
    return _get(f"/municipios/{municipio}/indicadores", ids=",".join(ids) if ids else None)


def obtener_ranking(indicador: str, criterio: str = "peor", limite: int = 3):
    return _get(f"/rankings/{indicador}", criterio=criterio, limite=limite)


def comparar_municipios(municipios: list[str], indicadores: list[str]):
    return _get("/comparacion", municipios=",".join(municipios), indicadores=",".join(indicadores))


# Mapa explícito de nombre a función: lo único que el modelo puede ejecutar.
FUNCIONES = {f.__name__: f for f in [listar_municipios, listar_indicadores, consultar_indicadores,
                                     obtener_ranking, comparar_municipios]}

INDICADORES = ["acceso_agua_pct", "recoleccion_residuos_pct", "reciclaje_pct",
               "areas_verdes_m2_hab", "pm25_ug_m3", "viajes_transporte_publico_pct"]


def _tool(nombre, descripcion, propiedades=None, requeridos=()):
    return {"type": "function", "function": {"name": nombre, "description": descripcion, "parameters": {
        "type": "object", "properties": propiedades or {}, "required": list(requeridos)}}}


# JSON Schema de cada herramienta: es lo que "lee" el modelo para decidir cuál usar.
TOOLS = [
    _tool("listar_municipios", "Lista los 9 municipios del AMG con su slug."),
    _tool("listar_indicadores", "Lista los indicadores disponibles con unidad y dirección deseable."),
    _tool("consultar_indicadores", "Valores 2025 de UN municipio.", {
        "municipio": {"type": "string", "description": "Slug del municipio, p. ej. 'tonala' o 'zapopan'"},
        "ids": {"type": "array", "items": {"type": "string", "enum": INDICADORES}, "description": "Indicadores a consultar (opcional)"},
    }, ["municipio"]),
    _tool("obtener_ranking", "Ranking de municipios para un indicador (los peores o los mejores).", {
        "indicador": {"type": "string", "enum": INDICADORES},
        "criterio": {"type": "string", "enum": ["peor", "mejor"]},
        "limite": {"type": "integer", "minimum": 1, "maximum": 9},
    }, ["indicador"]),
    _tool("comparar_municipios", "Compara 2 a 5 municipios en 1 a 6 indicadores.", {
        "municipios": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 5},
        "indicadores": {"type": "array", "items": {"type": "string", "enum": INDICADORES}, "minItems": 1, "maxItems": 6},
    }, ["municipios", "indicadores"]),
]


def ejecutar(nombre: str, argumentos: str) -> dict:
    """Valida lo que pidió el modelo y ejecuta la función real."""
    if nombre not in FUNCIONES:
        return {"error": f"La herramienta '{nombre}' no existe."}
    try:
        args = json.loads(argumentos or "{}")
        return FUNCIONES[nombre](**args)
    except (json.JSONDecodeError, TypeError) as e:
        return {"error": f"Argumentos inválidos para {nombre}: {e}"}
    except httpx.HTTPError as e:
        return {"error": f"No se pudo consultar la API: {e}"}
