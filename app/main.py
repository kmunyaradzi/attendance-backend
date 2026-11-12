from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import attendance, classes, students

app = FastAPI(title="Attendance Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classes.router, prefix="/classes", tags=["classes"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
