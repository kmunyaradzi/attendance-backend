from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClassBase(BaseModel):
    name: str
    teacher: str


class ClassCreate(ClassBase):
    pass


class ClassRead(ClassBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    class_id: int


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AttendanceBase(BaseModel):
    student_id: int
    attendance_date: date
    status: Literal["present", "absent", "late", "excused"]
    notes: str | None = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceRead(AttendanceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
