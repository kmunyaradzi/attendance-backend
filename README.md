# Attendance Backend

FastAPI + PostgreSQL backend for primary/high school attendance tracking.

## Scope (v1)
- Classes: ECD, Grade 1 – Grade 7
- Students belong to one class
- Attendance marked Monday–Friday, one record per student per day
- One teacher per class (recorded as text for now)

## Local setup
1. Create a virtual environment and activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set `DATABASE_URL`
4. Create the PostgreSQL database named in `DATABASE_URL` (for example, `attendance`)
5. `alembic upgrade head`
6. `uvicorn app.main:app --reload`

API docs at http://localhost:8000/docs