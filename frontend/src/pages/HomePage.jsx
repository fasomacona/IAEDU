import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div>
      <section className="hero">
        <h1>CodeMentor</h1>
        <p>
          Tutor de programación con IA que te guía con pistas progresivas
          sin revelar la solución. Diseñado para que aprendas haciendo y
          desarrolles pensamiento computacional.
        </p>
        <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
          <Link to="/estudiante" className="btn btn-primary">
            Empezar a practicar
          </Link>
          <Link to="/docente" className="btn btn-secondary">
            Panel docente
          </Link>
        </div>
      </section>

      <div className="features">
        <div className="card feature">
          <h3>1. Conceptual</h3>
          <p>
            La primera pista orienta al concepto involucrado (ciclos,
            condiciones, índices…) sin señalar líneas concretas.
          </p>
        </div>
        <div className="card feature">
          <h3>2. Ubicación</h3>
          <p>
            Señala la zona del error (rango de líneas o estructura) para
            que sepas dónde mirar, sin decir qué cambiar.
          </p>
        </div>
        <div className="card feature">
          <h3>3. Sugerencia</h3>
          <p>
            Indica el tipo de cambio necesario sin escribir nunca el
            código de la solución.
          </p>
        </div>
        <div className="card feature">
          <h3>Panel docente</h3>
          <p>
            Visualiza qué conceptos generan más bloqueos y cuántas pistas
            se solicitan por nivel en el grupo.
          </p>
        </div>
      </div>
    </div>
  );
}
