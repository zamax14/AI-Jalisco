from fastapi.testclient import TestClient

from api.main import INDICADORES, VALORES, app

c = TestClient(app)


def test_municipios_e_indicadores():
    r = c.get("/api/v1/municipios").json()
    assert len(r["data"]) == 9 and r["meta"]["is_mock"] is True
    assert len(c.get("/api/v1/indicadores").json()["data"]) == 6
    assert all(len(v) == 6 for v in VALORES.values())


def test_consulta_tolera_acentos_y_filtra():
    r = c.get("/api/v1/municipios/Tonalá/indicadores", params={"ids": "reciclaje_pct"}).json()
    assert r["data"]["municipio"]["slug"] == "tonala"
    assert r["data"]["valores"] == [{"indicador": "reciclaje_pct", "nombre": INDICADORES["reciclaje_pct"]["nombre"],
                                     "valor": VALORES["tonala"]["reciclaje_pct"], "unidad": "%"}]


def test_ranking_peor_respeta_direccion():
    # pm25: lo deseable es bajo, así que el peor es el más alto
    pm = [x["valor"] for x in c.get("/api/v1/rankings/pm25_ug_m3", params={"criterio": "peor", "limite": 9}).json()["data"]["ranking"]]
    assert pm == sorted(pm, reverse=True)
    # agua: lo deseable es alto, así que el peor es el más bajo
    agua = [x["valor"] for x in c.get("/api/v1/rankings/acceso_agua_pct").json()["data"]["ranking"]]
    assert len(agua) == 3 and agua == sorted(agua)
    assert agua[0] == min(v["acceso_agua_pct"] for v in VALORES.values())


def test_comparacion():
    r = c.get("/api/v1/comparacion", params={"municipios": "zapopan,Guadalajara", "indicadores": "acceso_agua_pct,areas_verdes_m2_hab"})
    filas = r.json()["data"]["comparacion"]
    assert filas[1]["valores"][1] == {"indicador": "areas_verdes_m2_hab", "nombre": "Áreas verdes por habitante",
                                      "valor": VALORES["guadalajara"]["areas_verdes_m2_hab"], "unidad": "m²/habitante"}


def test_errores():
    assert c.get("/api/v1/municipios/atlantida/indicadores").status_code == 404
    assert c.get("/api/v1/rankings/pib").status_code == 404
    assert c.get("/api/v1/rankings/pm25_ug_m3", params={"criterio": "regular"}).status_code == 422
    assert c.get("/api/v1/comparacion", params={"municipios": "zapopan", "indicadores": "pm25_ug_m3"}).status_code == 422
    assert c.get("/api/v1/comparacion", params={"municipios": "zapopan,tonala", "indicadores": "x"}).status_code == 404
