"""Etapa 4. Las mismas herramientas, ahora por MCP.

Ahora las herramientas no están en tools.py: las publica un servidor MCP y cualquier
cliente compatible puede descubrirlas (tools/list) y usarlas (tools/call).
"""
import asyncio
import json
import os

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.auth import BearerAuth

load_dotenv()
URL = os.environ["TALLER_BASE_URL"].rstrip("/") + "/mcp"


def titulo(texto):
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70)


async def main():
    async with Client(URL, auth=BearerAuth(os.environ["TALLER_TOKEN"])) as mcp:
        print(f"\nConectado a {URL}")

        titulo("tools/list: herramientas que publica el servidor")
        for tool in await mcp.list_tools():
            print(f"\n  {tool.name}")
            print(f"      {tool.description}")

        titulo("tools/call: obtener_ranking(indicador='pm25_ug_m3', criterio='peor', limite=3)")
        r = await mcp.call_tool("obtener_ranking", {"indicador": "pm25_ug_m3", "criterio": "peor", "limite": 3})
        print(json.dumps(r.structured_content, ensure_ascii=False, indent=2))


asyncio.run(main())
