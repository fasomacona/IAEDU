import { useState, useEffect, useCallback } from "react";
import Editor from "@monaco-editor/react";
import { api } from "../api";

const STORAGE_KEY = "codementor_student_id";

export default function StudentPage() {
  const [studentId, setStudentId] = useState(localStorage.getItem(STORAGE_KEY) || "");
  const [exercises, setExercises] = useState([]);
  const [current, setCurrent] = useState(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [hints, setHints] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [nextHintLevel, setNextHintLevel] = useState(1);

  // Crear o recuperar estudiante anónimo
  useEffect(() => {
    async function init() {
      if (!studentId) {
        try {
          const s = await api.createStudent();
          localStorage.setItem(STORAGE_KEY, s.anonymous_id);
          setStudentId(s.anonymous_id);
        } catch (e) {
          setError("No se pudo crear sesión de estudiante. ¿Está el backend en marcha?");
        }
      }
      try {
        const list = await api.getExercises();
        setExercises(list);
        if (list.length > 0) selectExercise(list[0]);
      } catch (e) {
        setError("No se pudieron cargar los ejercicios. Verifica el backend.");
      }
    }
    init();
  }, []);

  const selectExercise = useCallback(async (ex) => {
    setCurrent(ex);
    setResult(null);
    setHints({});
    setNextHintLevel(1);
    setError("");
    try {
      const full = await api.getExercise(ex.slug);
      setCode(full.starter_code || "# Escribe tu código aquí\n");
    } catch {
      setCode("# Escribe tu código aquí\n");
    }
  }, []);

  const handleSubmit = async () => {
    if (!current || !studentId) return;
    setLoading(true);
    setError("");
    setHints({});
    setNextHintLevel(1);
    try {
      const res = await api.submitCode(studentId, current.slug, code);
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleHint = async (level) => {
    if (!result || !current) return;
    setLoading(true);
    setError("");
    try {
      const h = await api.requestHint(studentId, result.submission_id, current.slug, level);
      setHints((prev) => ({ ...prev, [level]: h }));
      setNextHintLevel(level + 1);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="student-layout">
      <aside className="sidebar card">
        <h3 style={{ marginBottom: "0.75rem" }}>Ejercicios</h3>
        {exercises.map((ex) => (
          <div
            key={ex.slug}
            className={`exercise-item ${current?.slug === ex.slug ? "active" : ""}`}
            onClick={() => selectExercise(ex)}
          >
            <div className="title">{ex.title}</div>
            <div className="concepts">
              {(ex.concepts || []).join(" · ")}
            </div>
          </div>
        ))}
        {studentId && (
          <p style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "auto" }}>
            ID anónimo: {studentId}
          </p>
        )}
      </aside>

      <div className="editor-area">
        {current && (
          <div className="card" style={{ padding: "0.9rem 1.1rem" }}>
            <h2 style={{ fontSize: "1.15rem", marginBottom: "0.35rem" }}>
              {current.title}
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: 1.5 }}>
              {current.description}
            </p>
          </div>
        )}

        <div className="editor-wrapper">
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(v) => setCode(v || "")}
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </div>

        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading || !current}>
            {loading ? "Ejecutando…" : "Enviar y probar"}
          </button>
          {result && !result.passed && nextHintLevel <= 3 && (
            <button
              className="btn btn-warning"
              onClick={() => handleHint(nextHintLevel)}
              disabled={loading}
            >
              Pedir pista nivel {nextHintLevel}
            </button>
          )}
        </div>

        {error && (
          <div className="card" style={{ borderColor: "var(--danger)", color: "#fca5a5" }}>
            {error}
          </div>
        )}

        {result && (
          <div className="results-panel">
            <div className="card">
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
                <span className={`status-badge ${result.passed ? "status-pass" : "status-fail"}`}>
                  {result.passed ? "✓ Aprobado" : "✗ Falló"}
                </span>
                <span style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
                  {result.tests_passed}/{result.tests_total} tests · {Math.round(result.elapsed_ms)} ms
                </span>
              </div>
              {result.details?.length > 0 && (
                <ul style={{ fontSize: "0.85rem", color: "var(--text-muted)", paddingLeft: "1.2rem" }}>
                  {result.details.map((d, i) => (
                    <li key={i}>{d}</li>
                  ))}
                </ul>
              )}
              {result.static_findings?.length > 0 && (
                <div style={{ marginTop: "0.75rem" }}>
                  <strong style={{ fontSize: "0.85rem" }}>Análisis estático:</strong>
                  <ul style={{ fontSize: "0.85rem", color: "var(--text-muted)", paddingLeft: "1.2rem" }}>
                    {result.static_findings.map((f, i) => (
                      <li key={i}>
                        {f.lineno ? `L${f.lineno}: ` : ""}
                        {f.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="card">
              <h4 style={{ marginBottom: "0.5rem" }}>Pistas progresivas</h4>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.75rem" }}>
                Solicita las pistas en orden. El sistema nunca entrega el código de la solución.
              </p>
              {[1, 2, 3].map((lvl) =>
                hints[lvl] ? (
                  <div key={lvl} className="hint-box">
                    <div className="hint-level">
                      Nivel {lvl} — {lvl === 1 ? "Conceptual" : lvl === 2 ? "Ubicación" : "Sugerencia"}
                      {hints[lvl].filtered && " (filtrada)"}
                    </div>
                    <p style={{ fontSize: "0.9rem", lineHeight: 1.5 }}>{hints[lvl].hint}</p>
                  </div>
                ) : null
              )}
              {!hints[1] && !result.passed && (
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                  Aún no has solicitado pistas. Prueba primero a corregir con la información de los tests.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
