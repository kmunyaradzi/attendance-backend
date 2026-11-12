from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AttendanceRecord, Student
from app.schemas import AttendanceCreate, AttendanceRead

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("", response_model=list[AttendanceRead])
def list_attendance(
    attendance_date: date_type | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> list[AttendanceRecord]:
    query = db.query(AttendanceRecord)
    if attendance_date is not None:
        query = query.filter(AttendanceRecord.attendance_date == attendance_date)
    return query.order_by(AttendanceRecord.attendance_date.desc()).all()


@router.get("/student/{student_id}", response_model=list[AttendanceRead])
def list_student_attendance(student_id: int, db: Session = Depends(get_db)) -> list[AttendanceRecord]:
    return (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.student_id == student_id)
        .order_by(AttendanceRecord.attendance_date.desc())
        .all()
    )


@router.post("", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)) -> AttendanceRecord:
    student_exists = db.query(Student).filter(Student.id == payload.student_id).first()
    if student_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    record = AttendanceRecord(**payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attendance already recorded for this student on that date")
    db.refresh(record)
    return record
