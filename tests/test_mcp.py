import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient
from fastmcp import Client
from fastmcp.exceptions import ToolError

from api.main import app as api_app
from mcp_server import server

server.api = TestClient(api_app)  # la API real, en memoria
REST = server.api.get("/api/v1/rankings/pm25_ug_m3", params={"criterio": "peor", "limite": 3}).json()


def test_tools_list_y_call_igual_que_rest():
    async def run():
        async with Client(server.mcp) as c:
            nombres = sorted(t.name for t in await c.list_tools())
            assert nombres == ["comparar_municipios", "consultar_indicadores", "listar_indicadores", "listar_municipios", "obtener_ranking"]
            r = await c.call_tool("obtener_ranking", {"indicador": "pm25_ug_m3", "criterio": "peor", "limite": 3})
            assert r.structured_content == REST
            r = await c.call_tool("comparar_municipios", {"municipios": ["zapopan", "tonala"], "indicadores": ["reciclaje_pct"]})
            assert r.structured_content["meta"]["is_mock"] is True
            with pytest.raises(ToolError, match="no existe"):
                await c.call_tool("consultar_indicadores", {"municipio": "atlantida"})
    asyncio.run(run())


def test_http_exige_token():
    from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
    server.mcp.auth = StaticTokenVerifier({"secreto": {"client_id": "taller", "scopes": []}})
    app = server.mcp.http_app(path="/mcp", stateless_http=True, json_response=True)

    async def run():
        async with app.router.lifespan_context(app):
            t = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=t, base_url="http://127.0.0.1:8085") as h:
                init = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
                hdr = {"Accept": "application/json, text/event-stream"}
                assert (await h.post("/mcp", json=init, headers=hdr)).status_code == 401
                ok = await h.post("/mcp", json=init, headers={**hdr, "Authorization": "Bearer secreto"})
                assert ok.status_code != 401
    try:
        asyncio.run(run())
    finally:
        server.mcp.auth = None
