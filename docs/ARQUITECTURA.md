# Arquitectura de CodeMentor

## Componentes

1. **Frontend (Vite + React + Monaco Editor)**
   - Editor de código en el navegador
   - Flujo de envío y solicitud de pistas progresivas
   - Panel docente con estadísticas en tiempo real

2. **Backend (FastAPI)**
   - API REST
   - Sandbox de ejecución Python (subprocess + límites de recursos)
   - Análisis estático (AST)
   - Generación de pistas (LLM o mock basado en reglas)
   - Filtro post-generación anti-solución
   - Persistencia SQLite (envíos, pistas, conceptos)

3. **Banco de ejercicios**
   - 8 ejercicios de Fundamentos de Programación
   - Cada uno incluye: enunciado, starter code, tests unitarios, solución de referencia (nunca expuesta)

## Flujo de una pista

1. Estudiante envía código → tests + análisis estático
2. Si falla, puede pedir nivel 1 (conceptual)
3. Solo después puede pedir nivel 2 (ubicación)
4. Solo después nivel 3 (sugerencia específica)
5. El filtro bloquea cualquier respuesta que contenga código o frases de solución

## Seguridad del sandbox

- Timeout configurable
- Límite de memoria (resource)
- Directorio temporal aislado
- Sin acceso a red ni filesystem del host

## Extensión futura

- Soporte Java / C
- Más ejercicios y materias
- Visualizaciones de trayectorias de aprendizaje
- Publicación como recurso educativo abierto
