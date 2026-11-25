"""
Entorno de ejecución aislado (sandbox) para Python.
Usa subprocess con límites de tiempo y captura de salida.
En producción se recomienda un contenedor Docker o Pyodide.
"""
import subprocess
import tempfile
import os
import time
import resource
from typing import Tuple
from app.core.config import get_settings

settings = get_settings()


def _limit_resources():
    """Limita memoria y CPU del proceso hijo (Linux)."""
    try:
        # ~100 MB de memoria virtual
        resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))
        # Tiempo de CPU
        resource.setrlimit(resource.RLIMIT_CPU, (settings.sandbox_timeout_seconds, settings.sandbox_timeout_seconds))
    except Exception:
        pass


def run_python_code(code: str, timeout: int | None = None) -> Tuple[str, str, int, float]:
    """
    Ejecuta código Python de forma aislada.
    Returns: (stdout, stderr, returncode, elapsed_ms)
    """
    timeout = timeout or settings.sandbox_timeout_seconds
    start = time.perf_counter()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "student_code.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
                preexec_fn=_limit_resources if os.name == "posix" else None,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONPATH": "",
                    "HOME": tmpdir,
                },
            )
            elapsed = (time.perf_counter() - start) * 1000
            stdout = result.stdout[: settings.sandbox_max_output_chars]
            stderr = result.stderr[: settings.sandbox_max_output_chars]
            return stdout, stderr, result.returncode, elapsed
        except subprocess.TimeoutExpired:
            elapsed = (time.perf_counter() - start) * 1000
            return "", "Timeout: el código excedió el tiempo límite de ejecución.", -1, elapsed
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return "", f"Error de ejecución: {str(e)}", -2, elapsed


def run_tests(code: str, test_code: str, timeout: int | None = None) -> dict:
    """
    Ejecuta el código del estudiante junto con los tests unitarios.
    El test_code debe definir una función run_tests() que retorne (passed, total, details).
    """
    combined = f"""
{code}

# ---------- TESTS (no modificar) ----------
{test_code}

if __name__ == "__main__":
    try:
        result = run_tests()
        print("___TEST_RESULT___")
        print(result)
    except Exception as e:
        print("___TEST_RESULT___")
        print((0, 0, [str(e)]))
"""
    stdout, stderr, returncode, elapsed = run_python_code(combined, timeout=timeout or 8)

    passed, total, details = 0, 0, []
    if "___TEST_RESULT___" in stdout:
        try:
            # Extraer la tupla después del marcador
            after = stdout.split("___TEST_RESULT___")[-1].strip()
            # Evaluación segura limitada
            result = eval(after, {"__builtins__": {}})
            if isinstance(result, (list, tuple)) and len(result) >= 2:
                passed = int(result[0])
                total = int(result[1])
                details = list(result[2]) if len(result) > 2 else []
        except Exception:
            details = ["No se pudo interpretar el resultado de los tests"]
    else:
        details = [stderr or "Los tests no produjeron resultado"]

    return {
        "passed": passed,
        "total": total,
        "details": details,
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "elapsed_ms": elapsed,
        "all_passed": passed == total and total > 0,
    }
