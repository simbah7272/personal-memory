"""Pydantic schemas for data validation."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FinanceRecordCreate(BaseModel):
    """Schema for creating finance record."""
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    category: Optional[str] = None
    description: Optional[str] = None
    raw_text: Optional[str] = None
    record_date: date

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount has at most 2 decimal places."""
        return v.quantize(Decimal("0.01"))


class FinanceRecordResponse(BaseModel):
    """Schema for finance record response."""
    id: int
    type: str
    amount: Decimal
    category: Optional[str]
    description: Optional[str]
    record_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class HealthRecordCreate(BaseModel):
    """Schema for creating health record."""
    record_date: date
    sleep_hours: Optional[Decimal] = Field(None, ge=0, le=24, decimal_places=2)
    sleep_quality: Optional[str] = None
    wake_time: Optional[datetime] = None
    bed_time: Optional[datetime] = None
    mood: Optional[str] = None
    notes: Optional[str] = None
    raw_text: Optional[str] = None


class HealthRecordResponse(BaseModel):
    """Schema for health record response."""
    id: int
    record_date: date
    sleep_hours: Optional[Decimal]
    sleep_quality: Optional[str]
    mood: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkRecordCreate(BaseModel):
    """Schema for creating work record."""
    record_date: date
    task_name: str
    duration_hours: Decimal = Field(..., gt=0, decimal_places=2)
    value_description: Optional[str] = None
    tags: Optional[str] = None
    status: str = "completed"
    raw_text: Optional[str] = None

    @field_validator("duration_hours")
    @classmethod
    def validate_duration(cls, v):
        """Ensure duration has at most 2 decimal places."""
        return v.quantize(Decimal("0.01"))


class WorkRecordResponse(BaseModel):
    """Schema for work record response."""
    id: int
    record_date: date
    task_name: str
    duration_hours: Decimal
    value_description: Optional[str]
    tags: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class LeisureRecordCreate(BaseModel):
    """Schema for creating leisure record."""
    record_date: date
    activity: str
    duration_hours: Decimal = Field(..., gt=0, decimal_places=2)
    enjoyment_score: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    raw_text: Optional[str] = None

    @field_validator("duration_hours")
    @classmethod
    def validate_duration(cls, v):
        """Ensure duration has at most 2 decimal places."""
        return v.quantize(Decimal("0.01"))


class LeisureRecordResponse(BaseModel):
    """Schema for leisure record response."""
    id: int
    record_date: date
    activity: str
    duration_hours: Decimal
    enjoyment_score: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TimeLogCreate(BaseModel):
    """Schema for creating time log."""
    start_time: datetime
    end_time: Optional[datetime] = None
    category: Optional[str] = None
    activity: Optional[str] = None
    raw_text: Optional[str] = None


class TimeLogResponse(BaseModel):
    """Schema for time log response."""
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    category: Optional[str]
    activity: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
