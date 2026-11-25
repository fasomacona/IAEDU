# CodeMentor

**Tutor de programación con IA que guía sin revelar la solución**

Plataforma web colaborativa desarrollada por docentes y estudiantes del  
**TecNM: Tecnológico de Estudios Superiores de Chalco (TESCHA)** y el  
**Centro Universitario Valle de Chalco – Universidad Autónoma del Estado de México**.

## Características principales

- Editor de código en el navegador (Monaco)
- Entorno de ejecución aislado para Python
- Análisis estático + pruebas unitarias automáticas
- **Pistas progresivas en 3 niveles** (nunca entrega la solución completa):
  1. **Conceptual** – orienta al concepto involucrado
  2. **Ubicación** – señala la zona del error
  3. **Sugerencia específica** – indica el tipo de cambio sin escribir código
- Filtro post-generación que bloquea bloques de código o soluciones reconocibles
- Panel docente con agregación de errores, conceptos difíciles y conteo de pistas por nivel
- Banco de 8 ejercicios de Fundamentos de Programación (estructuras de control, funciones y listas)

## Requisitos

- Python 3.11+
- Node.js 18+
- (Opcional) API key de un modelo de lenguaje compatible con OpenAI (OpenAI, Grok, etc.)

## Instalación rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/CodeMentor.git
cd CodeMentor

# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edita y agrega tu OPENAI_API_KEY si deseas pistas reales

# Frontend
cd ../frontend
npm install
```

## Ejecución local

Terminal 1 – Backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 – Frontend:
```bash
cd frontend
npm run dev
```

Abre http://localhost:5173

## Estructura del proyecto

```
CodeMentor/
├── backend/                 # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/        # sandbox, static analysis, LLM hints, filter
│   │   └── db/
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Vite + React + Monaco
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── ...
│   └── package.json
├── exercises/               # 8 ejercicios + tests + soluciones de referencia (ocultas)
├── docs/
└── README.md
```

## Uso pedagógico

1. El estudiante elige un ejercicio y escribe código.
2. Envía → el sistema ejecuta tests + análisis estático.
3. Si hay errores, puede solicitar pistas **en orden** (nivel 1 → 2 → 3).
4. El sistema **nunca** entrega el código de la solución.
5. El docente ve en el panel qué conceptos generan más bloqueos.

## Consideraciones éticas (según el estudio)

- La herramienta es de apoyo formativo; no califica ni sanciona.
- Consentimiento informado y anonimización de datos.
- No se envían datos personales al modelo de lenguaje.
- El estudiante sabe cuándo recibe una pista generada por IA.
- Ejecución en entorno aislado.

## Licencia

MIT – Proyecto educativo interinstitucional.

## Autores

- Dr. Fabián Soberanes Martín
- Dra. Anabelem Soberanes Martín
- Dr. José Luis Castillo Mendoza

TecNM TESCHA · UAEM Valle de Chalco
