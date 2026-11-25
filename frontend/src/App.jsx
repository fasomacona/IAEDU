import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import StudentPage from "./pages/StudentPage";
import TeacherPage from "./pages/TeacherPage";
import HomePage from "./pages/HomePage";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="header">
          <div className="logo">
            <span className="logo-icon">{"</>"}</span>
            <span>CodeMentor</span>
          </div>
          <nav>
            <NavLink to="/" end>
              Inicio
            </NavLink>
            <NavLink to="/estudiante">Estudiante</NavLink>
            <NavLink to="/docente">Panel docente</NavLink>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/estudiante" element={<StudentPage />} />
            <Route path="/docente" element={<TeacherPage />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>
            CodeMentor · TESCHA &amp; UAEM Valle de Chalco · Tutor de programación
            que guía sin revelar la solución
          </p>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
