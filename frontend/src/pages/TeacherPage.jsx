import { useState, useEffect } from "react";
import { api } from "../api";

export default function TeacherPage() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [s, r] = await Promise.all([api.teacherStats(), api.recentSubmissions()]);
        setStats(s);
        setRecent(r);
      } catch (e) {
        setError("No se pudieron cargar las estadísticas. ¿Backend en marcha?");
      }
    }
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  if (error) {
    return <div className="card" style={{ color: "#fca5a5" }}>{error}</div>;
  }

  if (!stats) {
    return <div className="card">Cargando panel docente…</div>;
  }

  return (
    <div>
      <h2 style={{ marginBottom: "1.25rem" }}>Panel docente</h2>

      <div className="stats-grid">
        <div className="card stat-card">
          <div className="value">{stats.total_submissions}</div>
          <div className="label">Envíos totales</div>
        </div>
        <div className="card stat-card">
          <div className="value">{stats.pass_rate}%</div>
          <div className="label">Tasa de aprobación</div>
        </div>
        <div className="card stat-card">
          <div className="value">{stats.total_hints}</div>
          <div className="label">Pistas solicitadas</div>
        </div>
        <div className="card stat-card">
          <div className="value">{stats.hints_by_level[1] || 0}</div>
          <div className="label">Pistas nivel 1</div>
        </div>
        <div className="card stat-card">
          <div className="value">{stats.hints_by_level[2] || 0}</div>
          <div className="label">Pistas nivel 2</div>
        </div>
        <div className="card stat-card">
          <div className="value">{stats.hints_by_level[3] || 0}</div>
          <div className="label">Pistas nivel 3</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
        <div className="card">
          <h3 style={{ marginBottom: "0.75rem" }}>Conceptos con más dificultad</h3>
          {stats.top_concepts.length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
              Aún no hay datos de pistas.
            </p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Concepto</th>
                  <th>Veces</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_concepts.map((c) => (
                  <tr key={c.concept}>
                    <td>{c.concept.replace(/_/g, " ")}</td>
                    <td>{c.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: "0.75rem" }}>Envíos recientes</h3>
          {recent.length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Sin envíos aún.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Resultado</th>
                  <th>Tests</th>
                  <th>Hora</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((s) => (
                  <tr key={s.id}>
                    <td>{s.id}</td>
                    <td>
                      <span className={`status-badge ${s.passed ? "status-pass" : "status-fail"}`}>
                        {s.passed ? "OK" : "Fail"}
                      </span>
                    </td>
                    <td>
                      {s.tests_passed}/{s.tests_total}
                    </td>
                    <td style={{ fontSize: "0.8rem" }}>
                      {new Date(s.created_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
