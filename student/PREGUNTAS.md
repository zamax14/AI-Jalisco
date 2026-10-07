<h1 align="center">Guía de preguntas para el agente</h1>

<p align="center">
  <a href="#nivel-1-una-herramienta-una-respuesta">Nivel 1</a> ·
  <a href="#nivel-2-rankings-y-comparaciones">Nivel 2</a> ·
  <a href="#nivel-3-varias-herramientas-o-razonamiento">Nivel 3</a> ·
  <a href="#nivel-4-límites-el-agente-debe-decir-no-sé">Nivel 4</a> ·
  <a href="#nivel-5-errores-el-agente-no-debe-inventar">Nivel 5</a> ·
  <a href="#experimenta">Experimenta</a>
</p>

> [!IMPORTANT]
> Todas las cifras son **datos sintéticos de 2025** inventados para el taller. No son estadísticas oficiales.

<img src="../assets/alex-presentando.png" alt="Alex" width="150" align="right">

Ejecuta `python 03_agente.py` y prueba estas preguntas. En cada una, observa en las trazas:
- **qué herramienta eligió** el modelo (`Modelo eligió: ...`),
- **con qué argumentos** (`Argumentos: ...`),
- y si la **respuesta final usa exactamente los números** del `Resultado`.

<br clear="right">

## Qué hay en los datos

**Municipios (9):** Guadalajara, Zapopan, San Pedro Tlaquepaque, Tonalá, Tlajomulco de Zúñiga, El Salto, Juanacatlán, Ixtlahuacán de los Membrillos y Zapotlanejo.

| Indicador | Unidad | Lo deseable es… |
|---|---|---|
| Acceso a agua entubada (`acceso_agua_pct`) | % | alto |
| Recolección de residuos (`recoleccion_residuos_pct`) | % | alto |
| Residuos reciclados (`reciclaje_pct`) | % | alto |
| Áreas verdes por habitante (`areas_verdes_m2_hab`) | m²/habitante | alto |
| Concentración de PM2.5 (`pm25_ug_m3`) | µg/m³ | **bajo** |
| Viajes en transporte público (`viajes_transporte_publico_pct`) | % | alto |

---

## Nivel 1. Una herramienta, una respuesta
| Pregunta | Herramienta esperada | Respuesta correcta |
|---|---|---|
| ¿Cuánto reciclaje reporta Tonalá? | `consultar_indicadores` | 21.6 % |
| ¿Qué porcentaje de viviendas tiene agua entubada en El Salto? | `consultar_indicadores` | 78.7 % |
| ¿Cuántos metros cuadrados de área verde por habitante tiene Zapopan? | `consultar_indicadores` | 1.96 m²/hab |
| Dame todos los indicadores de Juanacatlán. | `consultar_indicadores` (sin `ids`) | 6 valores |
| ¿Qué municipios hay disponibles? | `listar_municipios` | los 9 de arriba |
| ¿Qué indicadores puedo consultar y en qué unidades? | `listar_indicadores` | los 6 de arriba |

## Nivel 2. Rankings y comparaciones
| Pregunta | Herramienta esperada | Respuesta correcta |
|---|---|---|
| ¿Cuáles son los 3 municipios con peor calidad del aire (PM2.5)? | `obtener_ranking` (peor) | El Salto 37.7, Tlaquepaque 32.7, Zapopan 32.4 µg/m³ |
| ¿Qué municipio recicla más? | `obtener_ranking` (mejor, 1) | Tonalá 21.6 % |
| ¿Cuáles son los 3 municipios con menos áreas verdes? | `obtener_ranking` (peor) | Zapopan 1.96, Guadalajara 3.32, El Salto 5.36 |
| ¿Dónde se usa más el transporte público? | `obtener_ranking` (mejor) | Zapopan 44.4, Guadalajara 44.1, Tonalá 42.4 % |
| Compara el acceso al agua y las áreas verdes entre Zapopan y Guadalajara. | `comparar_municipios` | Agua: 90.0 vs. 89.7 %; verdes: 1.96 vs. 3.32 m²/hab |
| Compara el reciclaje y el PM2.5 de Tonalá, El Salto y Zapotlanejo. | `comparar_municipios` | Reciclaje: 21.6 / 13.5 / 19.3 %; PM2.5: 29.3 / 37.7 / 22.3 µg/m³ |

> **Trampa del Nivel 2:** en PM2.5, «peor» significa el valor **más alto**; en los demás indicadores, el **más bajo**. La API ya lo resuelve con `direccion_deseable`. ¿El modelo lo explica bien?

## Nivel 3. Varias herramientas o razonamiento
| Pregunta | Qué observar |
|---|---|
| ¿Cuál es el municipio con peor PM2.5 y cómo está en transporte público? | Deberían ser dos pasos: `obtener_ranking` y **después** `consultar_indicadores` (El Salto: 37.7 µg/m³ y 27.2 %). A veces el modelo pide las dos herramientas a la vez y **adivina** el municipio antes de ver el ranking. ¿Por qué pasa? ¿Cómo lo arreglarías en el prompt? |
| ¿Qué municipio tiene el mejor acceso al agua y cuál el peor? ¿Cuánta diferencia hay? | Dos rankings o uno con límite 9; la resta: 94.8 − 78.7 = 16.1 puntos. |
| Identifica los 3 municipios con peor PM2.5 y sugiere acciones, separando los datos de las propuestas. | ¿Separa con claridad lo que viene de la API de lo que propone el modelo? |
| ¿Hay relación entre áreas verdes y PM2.5 en los datos? | ¿Consulta varios municipios antes de opinar? ¿Aclara que son datos simulados? |
| Haz un resumen de Guadalajara con sus fortalezas y debilidades. | Consulta los 6 indicadores; ¿usa bien la dirección deseable de cada uno? |

## Nivel 4. Límites: el agente debe decir "no sé"
| Pregunta | Comportamiento correcto |
|---|---|
| ¿Cuál será el nivel exacto de PM2.5 mañana? | No hay pronósticos: debe decirlo sin inventar. |
| ¿Cuánto reciclaje tenía Zapopan en 2018? | Solo hay datos de 2025. |
| ¿Cuál es la tasa de desempleo de Guadalajara? | Ese indicador no existe. |
| ¿Cuántos habitantes tiene Tlajomulco? | No hay datos de población. |
| ¿Estos datos son oficiales del IIEG? | No: son sintéticos. |

## Nivel 5. Errores: el agente no debe inventar
| Pregunta | Qué pasa |
|---|---|
| ¿Cuánto reciclaje tiene Atlántida? | Municipio inexistente: la API responde 404 y el agente debe decirlo. |
| ¿Cuánto reciclaje tiene Puerto Vallarta? | Es real, pero no está en el AMG ni en los datos. |
| Compara los 9 municipios en todos los indicadores. | La comparación acepta máximo 5 municipios: ¿cómo lo resuelve? |
| Dame el ranking de felicidad de los municipios. | Ese indicador no existe. |

---

## Experimenta
1. **Compara con `01_chat.py`:** haz las preguntas del Nivel 1 al chat sin herramientas. ¿Inventa cifras o reconoce que no las tiene?
2. **Escribe con errores:** «reciclaje de tonala», «agua en tlaquepaque», «pm 2.5 el salto». ¿El modelo encuentra la herramienta y el municipio correctos?
3. **Cambia el prompt:** en `03_agente.py`, borra «nunca inventes números» de `SISTEMA` y repite el Nivel 4. ¿Cambia algo?
4. **Quita una herramienta:** comenta `obtener_ranking` en `TOOLS` (`tools.py`) y pregunta por los peores en PM2.5. ¿Qué hace ahora?
5. **Revisa las trazas:** busca una respuesta donde la cifra final **no** coincida con el `Resultado`. Si la encuentras, ¡acabas de ver una alucinación!
