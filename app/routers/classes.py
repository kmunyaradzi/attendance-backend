from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Class

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
