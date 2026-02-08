"""Pydantic schemas for data validation."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from src.core.categories import (
    validate_category,
    validate_health_indicator,
    validate_goal_type,
)


# ============ Finance Schemas ============

class FinanceRecordCreate(BaseModel):
    """Schema for creating finance record."""
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    primary_category: str
    secondary_category: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None  # 现金/微信/支付宝/信用卡/其他
    merchant: Optional[str] = None  # 商家名称
    is_recurring: bool = False  # 是否周期性
    tags: Optional[List[str]] = None
    raw_text: Optional[str] = None
    record_date: date

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount has at most 2 decimal places."""
        return v.quantize(Decimal("0.01"))

    @field_validator("secondary_category")
    @classmethod
    def validate_secondary_category(cls, v, info):
        """Validate secondary category against configuration."""
        if v is None:
            return v

        primary = info.data.get("primary_category")
        if primary and not validate_category("finance", primary, v):
            raise ValueError(f"Invalid secondary category '{v}' for {primary}")
        return v


class FinanceRecordResponse(BaseModel):
    """Schema for finance record response."""
    id: int
    type: str
    amount: Decimal
    primary_category: str
    secondary_category: Optional[str]
    description: Optional[str]
    payment_method: Optional[str]
    merchant: Optional[str]
    is_recurring: bool
    tags: Optional[List[str]]
    record_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class FinanceRecordUpdate(BaseModel):
    """Schema for updating finance record."""
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    primary_category: Optional[str] = None
    secondary_category: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    merchant: Optional[str] = None
    is_recurring: Optional[bool] = None
    tags: Optional[List[str]] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount has at most 2 decimal places."""
        if v is not None:
            return v.quantize(Decimal("0.01"))
        return v


# ============ Health Schemas ============

class HealthRecordCreate(BaseModel):
    """Schema for creating health record."""
    record_date: date
    indicator_type: str  # sleep/exercise/diet/body/mental/medical
    indicator_name: str  # 具体指标名称
    value: Decimal = Field(..., decimal_places=2)
    unit: str
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    raw_text: Optional[str] = None

    @field_validator("indicator_type")
    @classmethod
    def validate_indicator_type(cls, v):
        """Validate indicator type."""
        if not validate_health_indicator(v):
            raise ValueError(f"Invalid indicator type '{v}'. Must be one of: sleep, exercise, diet, body, mental, medical")
        return v


class HealthRecordResponse(BaseModel):
    """Schema for health record response."""
    id: int
    record_date: date
    indicator_type: str
    indicator_name: str
    value: Decimal
    unit: str
    notes: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class HealthRecordUpdate(BaseModel):
    """Schema for updating health record."""
    indicator_type: Optional[str] = None
    indicator_name: Optional[str] = None
    value: Optional[Decimal] = Field(None, decimal_places=2)
    unit: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator("indicator_type")
    @classmethod
    def validate_indicator_type(cls, v):
        """Validate indicator type."""
        if v is not None and not validate_health_indicator(v):
            raise ValueError(f"Invalid indicator type '{v}'")
        return v


# ============ Work Schemas ============

class WorkRecordCreate(BaseModel):
    """Schema for creating work record."""
    record_date: date
    task_type: str  # 开发/会议/文档/学习/管理/协作
    task_name: str
    duration_hours: Decimal = Field(..., gt=0, decimal_places=2)
    value_description: Optional[str] = None
    project_id: Optional[int] = None
    priority: str = "medium"  # high/medium/low
    status: str = "completed"  # todo/in_progress/completed/cancelled
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Optional[List[str]] = None
    raw_text: Optional[str] = None

    @field_validator("duration_hours")
    @classmethod
    def validate_duration(cls, v):
        """Ensure duration has at most 2 decimal places."""
        return v.quantize(Decimal("0.01"))

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority."""
        if v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status."""
        if v not in ["todo", "in_progress", "completed", "cancelled"]:
            raise ValueError("Status must be one of: todo, in_progress, completed, cancelled")
        return v


class WorkRecordResponse(BaseModel):
    """Schema for work record response."""
    id: int
    record_date: date
    task_type: str
    task_name: str
    duration_hours: Decimal
    value_description: Optional[str]
    project_id: Optional[int]
    priority: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkRecordUpdate(BaseModel):
    """Schema for updating work record."""
    task_type: Optional[str] = None
    task_name: Optional[str] = None
    duration_hours: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    value_description: Optional[str] = None
    project_id: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Optional[List[str]] = None


# ============ Leisure Schemas ============

class LeisureRecordCreate(BaseModel):
    """Schema for creating leisure record."""
    record_date: date
    activity_type: str  # 运动/娱乐/户外/文化/放松
    activity: str
    duration_hours: Decimal = Field(..., gt=0, decimal_places=2)
    location: Optional[str] = None
    participants: Optional[List[str]] = None
    enjoyment_score: Optional[int] = Field(None, ge=1, le=5)
    cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    tags: Optional[List[str]] = None
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
    activity_type: str
    activity: str
    duration_hours: Decimal
    location: Optional[str]
    participants: Optional[List[str]]
    enjoyment_score: Optional[int]
    cost: Optional[Decimal]
    tags: Optional[List[str]]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LeisureRecordUpdate(BaseModel):
    """Schema for updating leisure record."""
    activity_type: Optional[str] = None
    activity: Optional[str] = None
    duration_hours: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    location: Optional[str] = None
    participants: Optional[List[str]] = None
    enjoyment_score: Optional[int] = Field(None, ge=1, le=5)
    cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


# ============ Learning Schemas ============

class LearningRecordCreate(BaseModel):
    """Schema for creating learning record."""
    record_date: date
    learning_type: str  # 阅读/课程/技能/认证/实践
    title: str
    duration_hours: Decimal = Field(..., gt=0, decimal_places=2)
    progress: int = Field(default=0, ge=0, le=100)  # 进度百分比
    source: Optional[str] = None  # 来源：书籍/视频/文章/课程/实践
    rating: Optional[int] = Field(None, ge=1, le=5)  # 评分
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    raw_text: Optional[str] = None

    @field_validator("duration_hours")
    @classmethod
    def validate_duration(cls, v):
        """Ensure duration has at most 2 decimal places."""
        return v.quantize(Decimal("0.01"))


class LearningRecordResponse(BaseModel):
    """Schema for learning record response."""
    id: int
    record_date: date
    learning_type: str
    title: str
    duration_hours: Decimal
    progress: int
    source: Optional[str]
    rating: Optional[int]
    notes: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class LearningRecordUpdate(BaseModel):
    """Schema for updating learning record."""
    learning_type: Optional[str] = None
    title: Optional[str] = None
    duration_hours: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    progress: Optional[int] = Field(None, ge=0, le=100)
    source: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


# ============ Social Schemas ============

class SocialRecordCreate(BaseModel):
    """Schema for creating social record."""
    record_date: date
    social_type: str  # 家人/朋友/同事/网络
    participants: Optional[List[str]] = None
    relationship_type: str  # 关系类型：家人/朋友/同事/网络
    duration_hours: Decimal = Field(..., gt=0, decimal_places=2)
    activity: str
    location: Optional[str] = None
    enjoyment_score: Optional[int] = Field(None, ge=1, le=5)
    cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    raw_text: Optional[str] = None

    @field_validator("duration_hours")
    @classmethod
    def validate_duration(cls, v):
        """Ensure duration has at most 2 decimal places."""
        return v.quantize(Decimal("0.01"))


class SocialRecordResponse(BaseModel):
    """Schema for social record response."""
    id: int
    record_date: date
    social_type: str
    participants: Optional[List[str]]
    relationship_type: str
    duration_hours: Decimal
    activity: str
    location: Optional[str]
    enjoyment_score: Optional[int]
    cost: Optional[Decimal]
    notes: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class SocialRecordUpdate(BaseModel):
    """Schema for updating social record."""
    social_type: Optional[str] = None
    participants: Optional[List[str]] = None
    relationship_type: Optional[str] = None
    duration_hours: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    activity: Optional[str] = None
    location: Optional[str] = None
    enjoyment_score: Optional[int] = Field(None, ge=1, le=5)
    cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


# ============ Goal Schemas ============

class GoalCreate(BaseModel):
    """Schema for creating goal."""
    goal_type: str  # health/finance/learning/work/life
    title: str
    description: Optional[str] = None
    target_value: Decimal = Field(..., gt=0, decimal_places=2)
    unit: str
    start_date: date
    target_date: date
    status: str = "active"  # active/completed/paused/cancelled
    frequency: Optional[str] = None  # daily/weekly/monthly/one_time
    tags: Optional[List[str]] = None

    @field_validator("goal_type")
    @classmethod
    def validate_goal_type(cls, v):
        """Validate goal type."""
        if not validate_goal_type(v):
            raise ValueError(f"Invalid goal type '{v}'. Must be one of: health, finance, learning, work, life")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status."""
        if v not in ["active", "completed", "paused", "cancelled"]:
            raise ValueError("Status must be one of: active, completed, paused, cancelled")
        return v


class GoalResponse(BaseModel):
    """Schema for goal response."""
    id: int
    goal_type: str
    title: str
    description: Optional[str]
    target_value: Decimal
    current_value: Decimal
    unit: str
    start_date: date
    target_date: date
    status: str
    frequency: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalUpdate(BaseModel):
    """Schema for updating goal."""
    goal_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    unit: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    frequency: Optional[str] = None
    tags: Optional[List[str]] = None


class GoalProgressCreate(BaseModel):
    """Schema for creating goal progress."""
    goal_id: int
    record_date: date
    value: Decimal = Field(..., decimal_places=2)
    notes: Optional[str] = None


class GoalProgressResponse(BaseModel):
    """Schema for goal progress response."""
    id: int
    goal_id: int
    record_date: date
    value: Decimal
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Time Log Schemas ============

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
