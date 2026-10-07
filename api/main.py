"""API REST de indicadores SINTÉTICOS del Área Metropolitana de Guadalajara (AMG).

Todos los números son inventados para el taller; NO son estadísticas oficiales.
Uso: uvicorn api.main:app --port 8084
"""
import json
import unicodedata
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Path as P, Query

DATA = Path(__file__).parent / "data"
MUNICIPIOS = {m["slug"]: m for m in json.loads((DATA / "municipios.json").read_text(encoding="utf-8"))}
INDICADORES = {i["id"]: i for i in json.loads((DATA / "indicadores.json").read_text(encoding="utf-8"))}
VALORES = json.loads((DATA / "valores_2025.json").read_text(encoding="utf-8"))

META = {
    "is_mock": True,
    "source": "Datos sintéticos para taller; NO son estadísticas oficiales",
    "reference_year": 2025,
}

app = FastAPI(
    title="API de indicadores AMG (datos sintéticos)",
    description="Indicadores **ficticios** de 9 municipios del Área Metropolitana de Guadalajara para el taller "
    "'De una API a un agente de IA'. Ningún número es estadística oficial del IIEG.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)


def respuesta(data):
    return {"data": data, "meta": META}


def slug(texto: str) -> str:
    """Convierte 'Tonalá' en 'tonala' y 'El Salto' en 'el-salto': tolera acentos, mayúsculas y espacios."""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "-".join(sin_acentos.lower().split())


def municipio(texto: str) -> dict:
    m = MUNICIPIOS.get(slug(texto))
    if not m:
        raise HTTPException(404, f"Municipio '{texto}' no existe. Usa uno de: {', '.join(MUNICIPIOS)}")
    return m


def indicador(texto: str) -> dict:
    i = INDICADORES.get(texto.strip().lower())
    if not i:
        raise HTTPException(404, f"Indicador '{texto}' no existe. Usa uno de: {', '.join(INDICADORES)}")
    return i


def lista(csv: str | None) -> list[str]:
    return [x for x in (csv or "").split(",") if x.strip()]


def valor(slug_m: str, ind: dict) -> dict:
    return {"indicador": ind["id"], "nombre": ind["nombre"], "valor": VALORES[slug_m][ind["id"]], "unidad": ind["unidad"]}


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/api/v1/municipios", summary="Lista los 9 municipios del AMG")
def listar_municipios():
    return respuesta(list(MUNICIPIOS.values()))


@app.get("/api/v1/indicadores", summary="Catálogo de indicadores (unidad, dirección deseable, ODS)")
def listar_indicadores():
    return respuesta(list(INDICADORES.values()))


@app.get("/api/v1/municipios/{slug_municipio}/indicadores", summary="Valores de un municipio")
def consultar_indicadores(
    slug_municipio: str = P(description="Slug o nombre del municipio, p. ej. `tonala` o `Tonalá`"),
    ids: str | None = Query(None, description="IDs de indicador separados por coma; si se omite, devuelve todos",
                            examples=["reciclaje_pct,pm25_ug_m3"]),
):
    m = municipio(slug_municipio)
    inds = [indicador(i) for i in lista(ids)] or list(INDICADORES.values())
    return respuesta({"municipio": m, "valores": [valor(m["slug"], i) for i in inds]})


@app.get("/api/v1/rankings/{indicador_id}", summary="Ranking de municipios para un indicador")
def obtener_ranking(
    indicador_id: str = P(description="ID del indicador, p. ej. `pm25_ug_m3`"),
    criterio: Literal["peor", "mejor"] = Query("peor", description="`peor` o `mejor`, según la dirección deseable del indicador"),
    limite: int = Query(3, ge=1, le=9, description="Cuántos municipios devolver (1 a 9)"),
):
    ind = indicador(indicador_id)
    # 'peor' en un indicador donde lo deseable es alto = los valores más bajos (y al revés).
    descendente = (ind["direccion_deseable"] == "alta") == (criterio == "mejor")
    orden = sorted(MUNICIPIOS, key=lambda s: VALORES[s][ind["id"]], reverse=descendente)[:limite]
    ranking = [{"posicion": n, "municipio": MUNICIPIOS[s], "valor": VALORES[s][ind["id"]]} for n, s in enumerate(orden, 1)]
    return respuesta({"indicador": ind, "criterio": criterio, "ranking": ranking})


@app.get("/api/v1/comparacion", summary="Tabla comparativa de 2 a 5 municipios y 1 a 6 indicadores")
def comparar_municipios(
    municipios: str = Query(..., description="2 a 5 municipios separados por coma", examples=["zapopan,tonala"]),
    indicadores: str = Query(..., description="1 a 6 IDs de indicador separados por coma", examples=["reciclaje_pct,pm25_ug_m3"]),
):
    ms, inds = lista(municipios), lista(indicadores)
    if not 2 <= len(ms) <= 5:
        raise HTTPException(422, "Indica entre 2 y 5 municipios separados por coma.")
    if not 1 <= len(inds) <= 6:
        raise HTTPException(422, "Indica entre 1 y 6 indicadores separados por coma.")
    ms, inds = [municipio(m) for m in ms], [indicador(i) for i in inds]
    filas = [{"municipio": m, "valores": [valor(m["slug"], i) for i in inds]} for m in ms]
    return respuesta({"indicadores": inds, "comparacion": filas})
