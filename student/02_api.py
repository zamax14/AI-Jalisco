"""Etapa 2. Consultar datos sin IA: la API ya resuelve el acceso a los datos."""
import json
import os
from urllib.parse import unquote

import httpx
from dotenv import load_dotenv

load_dotenv()
API = os.environ["TALLER_BASE_URL"].rstrip("/") + "/api/v1"


def mostrar(titulo, ruta, **params):
    r = httpx.get(API + ruta, params=params, timeout=15)
    print("=" * 70)
    print(f"  {titulo}")
    print(f"  GET {unquote(str(r.url))}  (HTTP {r.status_code})")
    print("=" * 70)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    print()


mostrar("Municipios disponibles", "/municipios")
mostrar("Reciclaje en Tonalá", "/municipios/tonala/indicadores", ids="reciclaje_pct")
mostrar("Los 3 municipios con peor PM2.5", "/rankings/pm25_ug_m3", criterio="peor", limite=3)
mostrar("Zapopan vs. Guadalajara: agua y áreas verdes", "/comparacion",
        municipios="zapopan,guadalajara", indicadores="acceso_agua_pct,areas_verdes_m2_hab")
