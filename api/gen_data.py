"""Genera los fixtures SINTÉTICOS de api/data/ (semilla fija: siempre los mismos números).

Uso: python api/gen_data.py
El resultado se guarda en git; la API solo lo lee.
"""
import json
import random
from pathlib import Path

DATA = Path(__file__).parent / "data"
FUENTE = "Datos sintéticos para taller"

MUNICIPIOS = [
    ("guadalajara", "Guadalajara"),
    ("zapopan", "Zapopan"),
    ("san-pedro-tlaquepaque", "San Pedro Tlaquepaque"),
    ("tonala", "Tonalá"),
    ("tlajomulco-de-zuniga", "Tlajomulco de Zúñiga"),
    ("el-salto", "El Salto"),
    ("juanacatlan", "Juanacatlán"),
    ("ixtlahuacan-de-los-membrillos", "Ixtlahuacán de los Membrillos"),
    ("zapotlanejo", "Zapotlanejo"),
]

# id, nombre, descripcion, unidad, direccion_deseable, ods, (min, max), decimales
INDICADORES = [
    ("acceso_agua_pct", "Acceso a agua entubada", "Porcentaje de viviendas con agua entubada dentro de la vivienda.",
     "%", "alta", "ODS 6", (78, 99), 1),
    ("recoleccion_residuos_pct", "Recolección de residuos", "Porcentaje de viviendas con servicio regular de recolección de residuos.",
     "%", "alta", "ODS 11", (70, 98), 1),
    ("reciclaje_pct", "Residuos reciclados", "Porcentaje de residuos sólidos urbanos que se reciclan.",
     "%", "alta", "ODS 12", (3, 22), 1),
    ("areas_verdes_m2_hab", "Áreas verdes por habitante", "Metros cuadrados de área verde pública por habitante.",
     "m²/habitante", "alta", "ODS 11", (1.5, 12), 2),
    ("pm25_ug_m3", "Concentración de PM2.5", "Promedio anual de partículas finas PM2.5 en el aire.",
     "µg/m³", "baja", "ODS 3, ODS 11", (14, 38), 1),
    ("viajes_transporte_publico_pct", "Viajes en transporte público", "Porcentaje de viajes diarios realizados en transporte público.",
     "%", "alta", "ODS 11", (12, 45), 1),
]


def main() -> None:
    rnd = random.Random(2025)
    DATA.mkdir(exist_ok=True)
    municipios = [{"slug": s, "nombre": n} for s, n in MUNICIPIOS]
    indicadores = [
        {"id": i, "nombre": n, "descripcion": d, "unidad": u, "anio": 2025,
         "direccion_deseable": dd, "ods": o, "fuente": FUENTE}
        for i, n, d, u, dd, o, _, _ in INDICADORES
    ]
    valores = {
        s: {i: round(rnd.uniform(lo, hi), dec) for i, *_, (lo, hi), dec in INDICADORES}
        for s, _ in MUNICIPIOS
    }
    for nombre, obj in [("municipios", municipios), ("indicadores", indicadores), ("valores_2025", valores)]:
        (DATA / f"{nombre}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
