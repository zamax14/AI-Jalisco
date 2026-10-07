"""Adaptador MCP (FastMCP): publica la API REST de indicadores como 5 herramientas MCP.

No lee los JSON ni tiene modelo: cada tool es una llamada HTTP a la API. Ofrece
capacidades; el agente es quien decide usarlas.
Uso: uvicorn mcp_server.server:app --port 8085  (endpoint en /mcp)
"""
import os

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

API_URL = os.getenv("API_URL", "http://127.0.0.1:8084")
TOKEN = os.getenv("WORKSHOP_TOKEN", "")
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "ai-jalisco.datzin.com.mx")

mcp = FastMCP(
    "Indicadores AMG (datos sintéticos)",
    instructions="Indicadores FICTICIOS de 2025 de 9 municipios del Área Metropolitana de Guadalajara. "
    "No son estadísticas oficiales.",
    auth=StaticTokenVerifier({TOKEN: {"client_id": "taller", "scopes": []}}) if TOKEN else None,
)
api = httpx.Client(base_url=API_URL, timeout=10)


def get(ruta: str, **params) -> dict:
    r = api.get(ruta, params={k: v for k, v in params.items() if v is not None})
    if r.status_code >= 400:
        raise ToolError(r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text)
    return r.json()


@mcp.tool
def listar_municipios() -> dict:
    """Lista los 9 municipios del AMG con su slug (identificador) y nombre."""
    return get("/api/v1/municipios")


@mcp.tool
def listar_indicadores() -> dict:
    """Lista el catálogo de indicadores: id, nombre, unidad, dirección deseable y ODS."""
    return get("/api/v1/indicadores")


@mcp.tool
def consultar_indicadores(municipio: str, ids: list[str] | None = None) -> dict:
    """Valores 2025 (sintéticos) de un municipio. `ids` filtra indicadores; si se omite, devuelve todos."""
    return get(f"/api/v1/municipios/{municipio}/indicadores", ids=",".join(ids) if ids else None)


@mcp.tool
def obtener_ranking(indicador: str, criterio: str = "peor", limite: int = 3) -> dict:
    """Ranking de municipios para un indicador. criterio='peor' o 'mejor' respeta su dirección deseable."""
    return get(f"/api/v1/rankings/{indicador}", criterio=criterio, limite=limite)


@mcp.tool
def comparar_municipios(municipios: list[str], indicadores: list[str]) -> dict:
    """Tabla comparativa de 2 a 5 municipios y 1 a 6 indicadores."""
    return get("/api/v1/comparacion", municipios=",".join(municipios), indicadores=",".join(indicadores))


app = mcp.http_app(
    path="/mcp",
    stateless_http=True,
    json_response=True,
    allowed_hosts=[PUBLIC_HOST, "127.0.0.1:*", "localhost:*"],
    allowed_origins=[f"https://{PUBLIC_HOST}"],
)
