from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Class
from app.routers.students import StudentRead

router = APIRouter()


class ClassCreate(BaseModel):
    name: str = Field(min_length=1)
    level: Literal["ecd", "primary"]


class ClassRead(BaseModel):
    id: int
    name: str
    level: str

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=ClassRead, status_code=status.HTTP_201_CREATED)
def create_class(payload: ClassCreate, db: Session = Depends(get_db)) -> Class:
    existing = db.query(Class).filter(Class.name == payload.name).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Class name already exists.",
        )

    record = Class(name=payload.name, level=payload.level)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[ClassRead])
def list_classes(db: Session = Depends(get_db)) -> list[Class]:
    return db.query(Class).order_by(Class.id).all()


@router.get("/{class_id}/students", response_model=list[StudentRead])
def list_students_in_class(
    class_id: int, db: Session = Depends(get_db)
) -> list[StudentRead]:
    class_record = (
        db.query(Class)
        .options(selectinload(Class.students))
        .filter(Class.id == class_id)
        .first()
    )
    if class_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found.",
        )

    return sorted(
        class_record.students,
        key=lambda student: (student.last_name, student.first_name),
    )
