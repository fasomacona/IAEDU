"""
Generación de pistas progresivas (3 niveles) usando un modelo de lenguaje
o un sistema de respaldo basado en reglas.
Nunca entrega la solución completa.
"""
import json
import httpx
from typing import List, Dict, Optional
from app.core.config import get_settings
from app.services.hint_filter import sanitize_hint

settings = get_settings()


LEVEL_DESCRIPTIONS = {
    1: {
        "name": "Conceptual",
        "instruction": (
            "Orienta al estudiante hacia el CONCEPTO involucrado. "
            "No menciones números de línea ni variables concretas. "
            "Habla de ideas generales (condiciones de terminación, alcance de variables, "
            "índices, casos límite, etc.). Máximo 2 oraciones."
        ),
    },
    2: {
        "name": "Ubicación",
        "instruction": (
            "Señala la ZONA del error (rango de líneas aproximado o la estructura: "
            "el ciclo, la condición, la función). No digas exactamente qué cambiar. "
            "Máximo 2 oraciones."
        ),
    },
    3: {
        "name": "Sugerencia específica",
        "instruction": (
            "Indica QUÉ TIPO de cambio hacer (actualizar una variable, revisar un índice, "
            "agregar una condición de borde) SIN escribir ninguna línea de código. "
            "Nunca muestres código. Máximo 2 oraciones."
        ),
    },
}


SYSTEM_PROMPT = """Eres CodeMentor, un tutor de programación que aplica andamiaje pedagógico.
Tu único objetivo es ayudar al estudiante a descubrir el error por sí mismo.
REGLAS ABSOLUTAS:
1. NUNCA entregues código de solución, ni completo ni fragmentado.
2. NUNCA escribas bloques ```python ni definiciones de funciones.
3. Responde SOLO con la pista del nivel solicitado.
4. Sé breve, claro y en español.
5. Si el estudiante ya pidió niveles anteriores, no repitas la misma información.
"""


async def generate_hint(
    level: int,
    exercise_title: str,
    exercise_description: str,
    student_code: str,
    test_details: List[str],
    static_findings: List[Dict],
    previous_hints: Optional[List[str]] = None,
) -> Dict:
    """
    Genera una pista del nivel indicado.
    Retorna {"hint": str, "concept_tags": str, "filtered": bool, "source": "llm"|"mock"}
    """
    if level not in (1, 2, 3):
        level = 1

    if settings.use_mock_hints or not settings.openai_api_key:
        hint, tags = _mock_hint(level, static_findings, test_details)
        safe = sanitize_hint(hint, level)
        return {
            "hint": safe,
            "concept_tags": tags,
            "filtered": safe != hint,
            "source": "mock",
        }

    # Construir prompt para el LLM
    findings_text = "\n".join(
        f"- [{f.get('type')}] línea {f.get('lineno')}: {f.get('message')} (concepto: {f.get('concept')})"
        for f in static_findings
    ) or "Ningún hallazgo estático relevante."

    tests_text = "\n".join(f"- {d}" for d in test_details[:8]) or "Sin detalles de tests."

    prev_text = ""
    if previous_hints:
        prev_text = "Pistas ya dadas al estudiante:\n" + "\n".join(f"- {h}" for h in previous_hints)

    user_prompt = f"""
Ejercicio: {exercise_title}
Descripción: {exercise_description}

Código del estudiante:
```
{student_code[:2500]}
```

Resultados de pruebas:
{tests_text}

Análisis estático:
{findings_text}

{prev_text}

Nivel de pista solicitado: {level} – {LEVEL_DESCRIPTIONS[level]['name']}
Instrucción específica: {LEVEL_DESCRIPTIONS[level]['instruction']}

Genera ÚNICAMENTE la pista de ese nivel. No agregues saludos ni explicaciones extra.
"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.openai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.4,
                    "max_tokens": 250,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            raw_hint = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # Fallback a mock si falla el LLM
        hint, tags = _mock_hint(level, static_findings, test_details)
        safe = sanitize_hint(hint, level)
        return {
            "hint": safe + f" (fallback por error de conexión: {type(e).__name__})",
            "concept_tags": tags,
            "filtered": False,
            "source": "mock",
        }

    safe = sanitize_hint(raw_hint, level)
    tags = _extract_concepts(static_findings, test_details)
    return {
        "hint": safe,
        "concept_tags": tags,
        "filtered": safe != raw_hint,
        "source": "llm",
    }


def _mock_hint(level: int, static_findings: List[Dict], test_details: List[str]) -> tuple[str, str]:
    """Pistas de respaldo basadas en reglas cuando no hay LLM."""
    concepts = []
    for f in static_findings:
        if f.get("concept"):
            concepts.append(f["concept"])

    # Heurísticas a partir de los mensajes de test
    test_lower = " ".join(test_details).lower()
    if "vacía" in test_lower or "empty" in test_lower or "[]" in test_lower:
        concepts.append("casos_limite")
    if "índice" in test_lower or "index" in test_lower or "range" in test_lower:
        concepts.append("indices")
    if "none" in test_lower or "nonetype" in test_lower:
        concepts.append("valores_nulos")
    if "ciclo" in test_lower or "loop" in test_lower or "while" in test_lower:
        concepts.append("ciclos_terminacion")

    concepts = list(dict.fromkeys(concepts))  # únicos preservando orden
    tags = ",".join(concepts) if concepts else "general"

    if level == 1:
        if "ciclos_terminacion" in concepts:
            return "Revisa cómo se comporta la condición de tu ciclo cuando la colección está vacía o cuando ya no hay más elementos.", tags
        if "casos_limite" in concepts:
            return "Piensa en los casos límite: ¿qué debería devolver la función cuando la entrada está vacía o tiene un solo elemento?", tags
        if "indices" in concepts:
            return "Recuerda cómo funcionan los índices en las listas de Python (empiezan en 0) y qué ocurre al salirte del rango.", tags
        if "sintaxis" in concepts:
            return "Hay un problema de sintaxis. Revisa paréntesis, dos puntos y la indentación.", tags
        return "Identifica el concepto principal que está fallando: condición, ciclo, índice o valor de retorno.", tags

    if level == 2:
        for f in static_findings:
            if f.get("lineno"):
                return f"El problema parece estar cerca de la línea {f['lineno']}. Revisa esa zona con calma.", tags
        if "ciclos_terminacion" in concepts:
            return "Fíjate en el cuerpo del ciclo y en la expresión que controla cuándo debe detenerse.", tags
        return "El error se concentra en la parte del código que procesa la estructura de datos principal del ejercicio.", tags

    # Nivel 3
    if "ciclos_terminacion" in concepts:
        return "La variable que controla el avance del ciclo no se actualiza dentro del cuerpo, o la condición nunca se vuelve falsa.", tags
    if "casos_limite" in concepts:
        return "Agrega una comprobación explícita para el caso en que la lista (o el argumento) esté vacío antes de procesar.", tags
    if "indices" in concepts:
        return "Verifica que el índice que usas nunca sea mayor o igual a la longitud de la lista.", tags
    return "Revisa si todas las variables que usas dentro de la función han sido inicializadas correctamente antes de utilizarlas.", tags


def _extract_concepts(static_findings: List[Dict], test_details: List[str]) -> str:
    concepts = [f.get("concept", "") for f in static_findings if f.get("concept")]
    test_lower = " ".join(test_details).lower()
    if "vacía" in test_lower or "empty" in test_lower:
        concepts.append("casos_limite")
    if "índice" in test_lower or "index" in test_lower:
        concepts.append("indices")
    return ",".join(dict.fromkeys(c for c in concepts if c))
