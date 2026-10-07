<p align="center">
  <img src="../assets/iieg-logo-morado.png" alt="IIEG" width="420">
</p>

<h1 align="center">Guía del alumno</h1>

<p align="center">
  Tu primer agente de IA en Python, en cuatro etapas.
  <br>
  <a href="#preparación">Preparación</a> ·
  <a href="#etapa-1-solo-habla">Etapas</a> ·
  <a href="#misiones">Misiones</a> ·
  <a href="#solución-de-problemas">Problemas</a> ·
  <a href="PREGUNTAS.md">Guía de preguntas</a>
</p>

> [!IMPORTANT]
> Todos los indicadores son **datos sintéticos** inventados para el taller. **No** son estadísticas oficiales del IIEG.

---

## Preparación

<img src="../assets/alex-laptop.png" alt="Alex preparando su computadora" width="190" align="right">

Te toma de **3 a 5 minutos**. Solo necesitas **Python 3.11 o superior** (revísalo con `python --version`). No necesitas Docker ni GPU: el modelo corre en el servidor del taller.

**1. Crea el entorno e instala las dependencias**

<table>
<tr><th>Linux / macOS</th><th>Windows (PowerShell)</th></tr>
<tr>
<td>

```bash
cd student
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

</td>
<td>

```powershell
cd student
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

</td>
</tr>
</table>

<br clear="right">

> [!TIP]
> Si PowerShell no te deja activar el entorno, ejecuta primero:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

**2. Pega el token del taller.** Abre el archivo `.env` y pon en `TALLER_TOKEN` el token que te dará el ponente:

```ini
TALLER_BASE_URL=https://ai-jalisco.datzin.com.mx
TALLER_TOKEN=pega-aqui-el-token-del-taller
OLLAMA_MODEL=qwen3:4b-instruct
# OLLAMA_MODEL=qwen3.5:0.8b    # más pequeño y rápido, pero se equivoca más
```

---

## Etapa 1. Solo habla

```bash
python 01_chat.py
```

Un chatbot **sin herramientas**. Pregúntale *«¿Cuánto reciclaje reporta Tonalá?»*. No tiene forma de saberlo: el modelo solo conoce lo que aprendió al entrenarse.

## Etapa 2. Consultar datos sin IA

```bash
python 02_api.py
```

Cuatro consultas a la API REST que imprimen el JSON de respuesta. **Los datos ya están ahí**; lo que falta es alguien que decida qué consultar a partir de una pregunta en lenguaje natural.

> [!NOTE]
> También puedes explorar la API desde el navegador: **[ai-jalisco.datzin.com.mx/api/docs](https://ai-jalisco.datzin.com.mx/api/docs)**

## Etapa 3. El modelo elige y el programa ejecuta

<img src="../assets/alex-agente.png" alt="Alex con su mochila de herramientas" width="210" align="right">

```bash
python 03_agente.py
```

Aquí nace el agente. En cada pregunta:

1. Tu programa manda la pregunta **y la lista de herramientas** (`TOOLS` en [`tools.py`](tools.py)).
2. El modelo responde: *«quiero usar `consultar_indicadores` con `{"municipio": "tonala"}`»*.
3. **Tu programa** valida la petición, llama a la API y le devuelve el resultado.
4. El modelo redacta la respuesta final con esos datos.

Fíjate en las trazas de cada paso: `Modelo eligió`, `Argumentos`, `GET` y `Resultado`.

<br clear="right">

## Etapa 4. Las mismas herramientas, ahora por MCP

```bash
python 04_mcp_demo.py
```

Las herramientas ya no viven en `tools.py`: las publica un **servidor MCP**. Cualquier cliente compatible las descubre (`tools/list`) y las usa (`tools/call`), sin copiar código. Compara el resultado con el `GET` de la etapa 2: son **los mismos números**.

<details>
<summary><b>Conectar otro cliente MCP</b> (por ejemplo, Claude Code)</summary>
<br>

El servidor usa **Streamable HTTP** en `https://ai-jalisco.datzin.com.mx/mcp` y pide el token en el header `Authorization`.

```bash
claude mcp add --transport http indicadores-amg https://ai-jalisco.datzin.com.mx/mcp --header "Authorization: Bearer <token>"
```

Clientes que aceptan configuración JSON:

```json
{
  "mcpServers": {
    "indicadores-amg": {
      "type": "http",
      "url": "https://ai-jalisco.datzin.com.mx/mcp",
      "headers": { "Authorization": "Bearer <token>" }
    }
  }
}
```
</details>

---

## Misiones

| | Misión | Pregunta para `03_agente.py` |
|:---:|---|---|
| **1** | Básica | ¿Cuánto reciclaje reporta Tonalá en los datos simulados de 2025? |
| **2** | Intermedia | Compara el acceso al agua y las áreas verdes entre Zapopan y Guadalajara, e indica las unidades. |
| **3** | Avanzada | Identifica los tres municipios con peor PM2.5 y sugiere acciones, separando los datos del ejercicio de las propuestas. |
| **4** | Límites | ¿Cuál será el nivel exacto de PM2.5 mañana? |
| **5** | Fallos | ¿Cuánto reciclaje tiene el municipio de Atlántida? |

> [!TIP]
> ¿Quieres más? En **[PREGUNTAS.md](PREGUNTAS.md)** hay una guía por niveles con las respuestas correctas, para comprobar que el agente no invente nada.

### Para experimentar

- Cambia el texto de `SISTEMA` en `03_agente.py` y observa cómo cambian las respuestas.
- En `tools.py`, cambia la `description` de una herramienta. ¿El modelo la sigue eligiendo bien?
- Quita una herramienta de `TOOLS`. ¿Qué responde el agente cuando ya no puede usarla?
- Cambia `OLLAMA_MODEL` en `.env` a `qwen3.5:0.8b` (unas 5 veces más pequeño) y repite las misiones 3 y 5. ¿Usa las herramientas o **inventa cifras**? Compara con las trazas.

---

## Solución de problemas

<details>
<summary><code>401</code> o «Token del taller inválido»</summary>
<br>
El token en <code>.env</code> está mal copiado. Revisa que no tenga espacios ni comillas.
</details>

<details>
<summary><code>KeyError: 'TALLER_BASE_URL'</code></summary>
<br>
No existe el archivo <code>.env</code> en la carpeta <code>student/</code>, o ejecutaste el script desde otra carpeta.
</details>

<details>
<summary>«No se pudo conectar al servidor» o <code>Name or service not known</code></summary>
<br>
No hay Internet, la URL de <code>.env</code> está mal escrita o tu red bloquea el dominio. Prueba abrir <a href="https://ai-jalisco.datzin.com.mx/healthz">ai-jalisco.datzin.com.mx/healthz</a> en el navegador.
</details>

<details>
<summary><code>429</code> o «servidor ocupado»</summary>
<br>
Hay muchas peticiones a la vez. Espera unos segundos y vuelve a intentar.
</details>

<details>
<summary>Tarda mucho o hay timeout</summary>
<br>
El modelo está atendiendo a todo el grupo. Reintenta con una pregunta más corta.
</details>

<details>
<summary>«Máximo 40 mensajes por conversación»</summary>
<br>
La conversación creció demasiado. Escribe <code>salir</code> y vuelve a ejecutar el programa.
</details>

<details>
<summary><code>ModuleNotFoundError</code></summary>
<br>
Falta activar el entorno virtual: <code>source .venv/bin/activate</code> (Linux/macOS) o <code>.\.venv\Scripts\Activate.ps1</code> (Windows).
</details>

---

<p align="center">
  <img src="../assets/iieg-logo-gris.png" alt="IIEG" width="220">
</p>
