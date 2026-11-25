"""
Carga de ejercicios desde la carpeta exercises/.
Cada ejercicio tiene: enunciado, tests, solución de referencia (nunca expuesta).
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional

# Ruta relativa al backend → ../exercises
EXERCISES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "exercises"


def list_exercises() -> List[Dict]:
    """Lista metadatos de todos los ejercicios (sin tests ni solución)."""
    result = []
    if not EXERCISES_DIR.exists():
        return result
    for path in sorted(EXERCISES_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        result.append({
            "slug": data["slug"],
            "title": data["title"],
            "description": data["description"],
            "concepts": data.get("concepts", []),
            "difficulty": data.get("difficulty", 1),
            "order": data.get("order", 0),
        })
    return sorted(result, key=lambda x: x["order"])


def get_exercise(slug: str) -> Optional[Dict]:
    """Devuelve el ejercicio completo (incluye test_code, NO la solución)."""
    path = EXERCISES_DIR / f"{slug}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Nunca devolvemos reference_solution al frontend
    data.pop("reference_solution", None)
    return data


def get_test_code(slug: str) -> Optional[str]:
    ex = get_exercise(slug)
    if not ex:
        return None
    return ex.get("test_code")
