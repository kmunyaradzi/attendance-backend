from fastapi import FastAPI

from app.routers import classes, students

app = FastAPI(title="Attendance Backend", version="0.1.0")

app.include_router(classes.router, prefix="/classes", tags=["classes"])
app.include_router(students.router, prefix="/students", tags=["students"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
