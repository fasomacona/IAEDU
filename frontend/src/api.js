const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Error de red");
  }
  return res.json();
}

export const api = {
  createStudent: (group_name = "general", institution = "TESCHA") =>
    request("/students", {
      method: "POST",
      body: JSON.stringify({ group_name, institution }),
    }),

  getExercises: () => request("/exercises"),

  getExercise: (slug) => request(`/exercises/${slug}`),

  submitCode: (student_id, exercise_slug, code) =>
    request("/submit", {
      method: "POST",
      body: JSON.stringify({ student_id, exercise_slug, code }),
    }),

  requestHint: (student_id, submission_id, exercise_slug, level) =>
    request("/hints/v2", {
      method: "POST",
      body: JSON.stringify({ student_id, submission_id, exercise_slug, level }),
    }),

  teacherStats: () => request("/teacher/stats"),

  recentSubmissions: () => request("/teacher/recent-submissions"),
};
