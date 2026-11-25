"""
Análisis estático básico del código del estudiante.
Detecta errores de sintaxis, estilos simples y patrones problemáticos.
"""
import ast
import re
from typing import List, Dict


def analyze_code(code: str) -> List[Dict]:
    """
    Retorna lista de hallazgos:
    [{"type": "syntax"|"style"|"logic_pattern", "message": str, "lineno": int|None, "concept": str}]
    """
    findings = []

    # 1. Sintaxis
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        findings.append({
            "type": "syntax",
            "message": f"Error de sintaxis: {e.msg}",
            "lineno": e.lineno,
            "concept": "sintaxis",
        })
        return findings  # Sin AST no podemos continuar

    # 2. Patrones de estilo / buenas prácticas
    findings.extend(_check_style(code, tree))

    # 3. Patrones lógicos comunes en fundamentos
    findings.extend(_check_logic_patterns(code, tree))

    return findings


def _check_style(code: str, tree: ast.AST) -> List[Dict]:
    findings = []
    lines = code.splitlines()

    # Variables de una sola letra excesivas (excepto i,j,k,n,x,y comunes)
    single_letter = re.findall(r"\b([a-z])\s*=", code)
    common = {"i", "j", "k", "n", "x", "y", "a", "b"}
    suspicious = [v for v in single_letter if v not in common]
    if len(suspicious) >= 3:
        findings.append({
            "type": "style",
            "message": "Hay varias variables de una sola letra. Considera nombres más descriptivos.",
            "lineno": None,
            "concept": "estilo_nombres",
        })

    # Código muy anidado
    max_depth = _max_nesting(tree)
    if max_depth >= 5:
        findings.append({
            "type": "style",
            "message": f"El anidamiento es profundo (nivel {max_depth}). Considera extraer funciones.",
            "lineno": None,
            "concept": "estructura",
        })

    # Líneas muy largas
    for i, line in enumerate(lines, 1):
        if len(line) > 100:
            findings.append({
                "type": "style",
                "message": "Línea demasiado larga (>100 caracteres).",
                "lineno": i,
                "concept": "estilo",
            })
            break

    return findings


def _check_logic_patterns(code: str, tree: ast.AST) -> List[Dict]:
    findings = []

    # Bucles while True sin break evidente
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                if not has_break:
                    findings.append({
                        "type": "logic_pattern",
                        "message": "Bucle while True sin break aparente. Revisa la condición de terminación.",
                        "lineno": getattr(node, "lineno", None),
                        "concept": "ciclos_terminacion",
                    })

        # if-else vacío
        if isinstance(node, ast.If):
            if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                findings.append({
                    "type": "logic_pattern",
                    "message": "Cuerpo de if vacío o solo 'pass'.",
                    "lineno": getattr(node, "lineno", None),
                    "concept": "condicionales",
                })

    # Variable usada antes de asignación (heurística simple)
    # (análisis completo de alcance es más complejo; aquí solo avisamos patrones comunes)
    if "for " in code and " in " in code:
        # Detectar posible modificación de la lista mientras se itera
        if re.search(r"for\s+\w+\s+in\s+(\w+).*?\1\.(append|remove|pop|insert)", code, re.DOTALL):
            findings.append({
                "type": "logic_pattern",
                "message": "Posible modificación de la lista mientras se itera sobre ella.",
                "lineno": None,
                "concept": "listas",
            })

    return findings


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    max_d = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef)):
            max_d = max(max_d, _max_nesting(child, depth + 1))
        else:
            max_d = max(max_d, _max_nesting(child, depth))
    return max_d
