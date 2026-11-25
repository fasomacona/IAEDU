from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
import uuid
import json

from app.db.database import get_db
from app.models.models import Student, Submission, HintRequest, Exercise
from app.services.exercises import list_exercises, get_exercise, get_test_code
from app.services.sandbox import run_tests
from app.services.static_analysis import analyze_code
from app.services.hint_generator import generate_hint

router = APIRouter()


# ---------- Schemas ----------
class StudentCreate(BaseModel):
    group_name: str = "general"
    institution: str = "TESCHA"


class CodeSubmit(BaseModel):
    student_id: str          # anonymous_id
    exercise_slug: str
    code: str


class HintRequestIn(BaseModel):
    student_id: str
    submission_id: int
    level: int               # 1, 2 or 3


# ---------- Students ----------
@router.post("/students")
async def create_student(body: StudentCreate, db: AsyncSession = Depends(get_db)):
    anon = str(uuid.uuid4())[:12]
    student = Student(anonymous_id=anon, group_name=body.group_name, institution=body.institution)
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return {"anonymous_id": student.anonymous_id, "id": student.id}


@router.get("/students/{anonymous_id}")
async def get_student(anonymous_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.anonymous_id == anonymous_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "Estudiante no encontrado")
    return {
        "anonymous_id": student.anonymous_id,
        "group_name": student.group_name,
        "institution": student.institution,
    }


# ---------- Exercises ----------
@router.get("/exercises")
async def get_exercises():
    return list_exercises()


@router.get("/exercises/{slug}")
async def get_one_exercise(slug: str):
    ex = get_exercise(slug)
    if not ex:
        raise HTTPException(404, "Ejercicio no encontrado")
    # Asegurar que no se filtre la solución
    ex.pop("reference_solution", None)
    return ex


# ---------- Submit code ----------
@router.post("/submit")
async def submit_code(body: CodeSubmit, db: AsyncSession = Depends(get_db)):
    # Buscar estudiante
    result = await db.execute(select(Student).where(Student.anonymous_id == body.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "Estudiante no encontrado. Crea una sesión primero.")

    exercise = get_exercise(body.exercise_slug)
    if not exercise:
        raise HTTPException(404, "Ejercicio no encontrado")

    test_code = get_test_code(body.exercise_slug)
    if not test_code:
        raise HTTPException(500, "Tests no disponibles para este ejercicio")

    # Análisis estático
    static = analyze_code(body.code)

    # Ejecutar tests
    test_result = run_tests(body.code, test_code)

    # Guardar submission
    sub = Submission(
        student_id=student.id,
        exercise_id=0,  # se puede mapear después si se cargan en DB
        code=body.code,
        passed=test_result["all_passed"],
        tests_passed=test_result["passed"],
        tests_total=test_result["total"],
        static_errors=json.dumps(static, ensure_ascii=False),
        execution_time_ms=test_result["elapsed_ms"],
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)

    return {
        "submission_id": sub.id,
        "passed": test_result["all_passed"],
        "tests_passed": test_result["passed"],
        "tests_total": test_result["total"],
        "details": test_result["details"],
        "static_findings": static,
        "elapsed_ms": test_result["elapsed_ms"],
        "stderr": test_result["stderr"] if not test_result["all_passed"] else "",
    }


# ---------- Hints ----------
@router.post("/hints")
async def request_hint(body: HintRequestIn, db: AsyncSession = Depends(get_db)):
    if body.level not in (1, 2, 3):
        raise HTTPException(400, "El nivel debe ser 1, 2 o 3")

    result = await db.execute(select(Student).where(Student.anonymous_id == body.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "Estudiante no encontrado")

    result = await db.execute(select(Submission).where(Submission.id == body.submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(404, "Envío no encontrado")

    # Verificar que el estudiante solo pueda pedir el siguiente nivel en orden
    prev = await db.execute(
        select(HintRequest)
        .where(HintRequest.submission_id == body.submission_id)
        .order_by(HintRequest.level)
    )
    previous = prev.scalars().all()
    max_level = max([h.level for h in previous], default=0)
    if body.level > max_level + 1:
        raise HTTPException(400, f"Debes solicitar primero el nivel {max_level + 1}")

    # Obtener ejercicio (necesitamos el slug; lo guardamos en static o lo buscamos)
    # Para simplificar, el frontend envía el slug en un campo extra o lo inferimos.
    # Aquí usamos un campo auxiliar: el frontend debe haber guardado el slug.
    # Solución práctica: guardar el slug en el código de static_errors o añadir columna.
    # Por ahora asumimos que el frontend vuelve a enviar el slug en un header o lo buscamos.
    # Mejor: añadir exercise_slug al body.
    raise HTTPException(501, "Usar endpoint /hints/v2 con exercise_slug")


class HintRequestV2(BaseModel):
    student_id: str
    submission_id: int
    exercise_slug: str
    level: int


@router.post("/hints/v2")
async def request_hint_v2(body: HintRequestV2, db: AsyncSession = Depends(get_db)):
    if body.level not in (1, 2, 3):
        raise HTTPException(400, "El nivel debe ser 1, 2 o 3")

    result = await db.execute(select(Student).where(Student.anonymous_id == body.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(404, "Estudiante no encontrado")

    result = await db.execute(select(Submission).where(Submission.id == body.submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(404, "Envío no encontrado")

    # Orden de pistas
    prev = await db.execute(
        select(HintRequest)
        .where(HintRequest.submission_id == body.submission_id)
        .order_by(HintRequest.level)
    )
    previous_hints = prev.scalars().all()
    max_level = max([h.level for h in previous_hints], default=0)
    if body.level > max_level + 1:
        raise HTTPException(400, f"Debes solicitar primero el nivel {max_level + 1}")
    if any(h.level == body.level for h in previous_hints):
        # Ya se pidió este nivel → devolver el mismo
        existing = next(h for h in previous_hints if h.level == body.level)
        return {
            "level": existing.level,
            "hint": existing.hint_text,
            "concept_tags": existing.concept_tags,
            "filtered": existing.filtered,
            "source": "cached",
        }

    exercise = get_exercise(body.exercise_slug)
    if not exercise:
        raise HTTPException(404, "Ejercicio no encontrado")

    static = json.loads(submission.static_errors or "[]")
    # Recuperar detalles de tests del último envío (no los guardamos, se re-ejecutan o se simplifican)
    test_details = []  # se puede mejorar guardándolos

    prev_texts = [h.hint_text for h in previous_hints]

    hint_data = await generate_hint(
        level=body.level,
        exercise_title=exercise["title"],
        exercise_description=exercise["description"],
        student_code=submission.code,
        test_details=test_details,
        static_findings=static,
        previous_hints=prev_texts,
    )

    hr = HintRequest(
        student_id=student.id,
        submission_id=submission.id,
        exercise_id=0,
        level=body.level,
        hint_text=hint_data["hint"],
        concept_tags=hint_data["concept_tags"],
        filtered=hint_data["filtered"],
    )
    db.add(hr)
    await db.commit()
    await db.refresh(hr)

    return {
        "level": body.level,
        "hint": hint_data["hint"],
        "concept_tags": hint_data["concept_tags"],
        "filtered": hint_data["filtered"],
        "source": hint_data["source"],
    }


# ---------- Teacher panel ----------
@router.get("/teacher/stats")
async def teacher_stats(db: AsyncSession = Depends(get_db)):
    # Total submissions
    total_subs = await db.scalar(select(func.count(Submission.id)))
    total_passed = await db.scalar(select(func.count(Submission.id)).where(Submission.passed == True))
    total_hints = await db.scalar(select(func.count(HintRequest.id)))

    # Hints by level
    hints_by_level = {}
    for level in (1, 2, 3):
        count = await db.scalar(
            select(func.count(HintRequest.id)).where(HintRequest.level == level)
        )
        hints_by_level[level] = count or 0

    # Concept tags frequency
    result = await db.execute(select(HintRequest.concept_tags))
    tags_raw = result.scalars().all()
    concept_count: dict[str, int] = {}
    for tags in tags_raw:
        if not tags:
            continue
        for t in tags.split(","):
            t = t.strip()
            if t:
                concept_count[t] = concept_count.get(t, 0) + 1

    top_concepts = sorted(concept_count.items(), key=lambda x: -x[1])[:10]

    return {
        "total_submissions": total_subs or 0,
        "total_passed": total_passed or 0,
        "pass_rate": round((total_passed or 0) / (total_subs or 1) * 100, 1),
        "total_hints": total_hints or 0,
        "hints_by_level": hints_by_level,
        "top_concepts": [{"concept": c, "count": n} for c, n in top_concepts],
    }


@router.get("/teacher/recent-submissions")
async def recent_submissions(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Submission)
        .order_by(Submission.created_at.desc())
        .limit(limit)
    )
    subs = result.scalars().all()
    return [
        {
            "id": s.id,
            "passed": s.passed,
            "tests_passed": s.tests_passed,
            "tests_total": s.tests_total,
            "created_at": s.created_at.isoformat(),
        }
        for s in subs
    ]
