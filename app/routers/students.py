from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Class, Student

router = APIRouter()


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    class_id: int
    dob: date | None = None


class StudentRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    class_id: int
    dob: date | None

    model_config = ConfigDict(from_attributes=True)


class StudentCreateResponse(StudentRead):
    warning: str | None = None


@router.post(
    "",
    response_model=StudentCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    payload: StudentCreate, db: Session = Depends(get_db)
) -> StudentCreateResponse:
    class_exists = db.query(Class).filter(Class.id == payload.class_id).first()
    if class_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found.",
        )

    duplicate = (
        db.query(Student)
        .filter(
            Student.first_name == payload.first_name,
            Student.last_name == payload.last_name,
            Student.class_id == payload.class_id,
        )
        .first()
    )
    warning = (
        "A student with the same name already exists in this class."
        if duplicate is not None
        else None
    )

    record = Student(
        first_name=payload.first_name,
        last_name=payload.last_name,
        class_id=payload.class_id,
        dob=payload.dob,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return StudentCreateResponse(
        id=record.id,
        first_name=record.first_name,
        last_name=record.last_name,
        full_name=record.full_name,
        class_id=record.class_id,
        dob=record.dob,
        warning=warning,
    )


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)) -> Student:
    record = db.query(Student).filter(Student.id == student_id).first()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    return record
