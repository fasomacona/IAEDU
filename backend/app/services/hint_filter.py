"""
Filtro post-generación que bloquea cualquier respuesta que contenga
bloques de código completos o soluciones reconocibles.
"""
import re
from typing import Tuple


# Patrones que indican que se está entregando código de solución
BLOCKED_PATTERNS = [
    r"```python",                    # bloque markdown de código
    r"```\s*\n",                     # cualquier bloque de código
    r"def\s+\w+\s*\([^)]*\):\s*\n\s+",  # definición de función completa
    r"for\s+\w+\s+in\s+.*:\s*\n\s+\w+",  # bucle completo con cuerpo
    r"while\s+.*:\s*\n\s+\w+",
    r"if\s+.*:\s*\n\s+\w+.*\n\s*else:",
    r"return\s+\w+\s*\+",            # return con expresión compleja
    r"print\s*\(\s*f?[\"']",         # print de resultados típicos de solución
]

# Frases que el modelo a veces usa para "mostrar" la solución
SOLUTION_PHRASES = [
    "aquí está el código",
    "la solución es",
    "el código correcto sería",
    "puedes usar este código",
    "copia este fragmento",
    "la función completa",
    "implementación completa",
]


def is_solution_leak(text: str) -> Tuple[bool, str]:
    """
    Devuelve (es_filtrado, texto_seguro).
    Si detecta fuga de solución, sustituye por un mensaje genérico de nivel inferior.
    """
    lower = text.lower()

    for phrase in SOLUTION_PHRASES:
        if phrase in lower:
            return True, (
                "He detectado que la respuesta anterior podía revelar demasiado. "
                "Intenta primero con la pista del nivel anterior o revisa la condición "
                "y las variables involucradas."
            )

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            return True, (
                "La pista generada contenía código demasiado específico y fue bloqueada. "
                "Revisa el concepto indicado y prueba un cambio pequeño. "
                "Si necesitas más ayuda, solicita la siguiente pista de nivel inferior."
            )

    # Bloquear líneas que parezcan código ejecutable puro (heurística)
    lines = text.splitlines()
    code_like = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^(def |class |for |while |if |elif |else:|return |print\(|import )", stripped):
            code_like += 1
    if code_like >= 3:
        return True, (
            "La respuesta contenía demasiadas líneas de código y fue filtrada. "
            "Enfócate en el concepto o en la zona del error sin escribir la solución completa."
        )

    return False, text


def sanitize_hint(text: str, level: int) -> str:
    """Aplica el filtro y, si es necesario, degrada el nivel de ayuda."""
    filtered, safe = is_solution_leak(text)
    if filtered:
        return safe
    # Limitar longitud excesiva
    if len(safe) > 600:
        safe = safe[:580] + "…"
    return safe.strip()
