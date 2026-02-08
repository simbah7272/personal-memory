"""SQLAlchemy ORM models."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, Integer, String, Text, Time, Numeric, TIMESTAMP, ForeignKey, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    """User model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feishu_user_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Shanghai")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    finance_records: Mapped[list["FinanceRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    health_records: Mapped[list["HealthRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    work_records: Mapped[list["WorkRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    leisure_records: Mapped[list["LeisureRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    learning_records: Mapped[list["LearningRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    social_records: Mapped[list["SocialRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    goal_progress: Mapped[list["GoalProgress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    time_logs: Mapped[list["TimeLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class FinanceRecord(Base):
    """Finance record model with primary and secondary categories."""
    __tablename__ = "finance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(10))  # 'income' | 'expense'
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    primary_category: Mapped[str] = mapped_column(String(50))  # Primary category
    secondary_category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Secondary category
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 现金/微信/支付宝/信用卡/其他
    merchant: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 商家名称
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否周期性
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 标签数组
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    record_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="finance_records")


class HealthRecord(Base):
    """Health record model with multi-indicator system."""
    __tablename__ = "health_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    indicator_type: Mapped[str] = mapped_column(String(20))  # sleep/exercise/diet/body/mental/medical
    indicator_name: Mapped[str] = mapped_column(String(50))  # 具体指标名称：如"体重"、"跑步时长"
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # 数值
    unit: Mapped[str] = mapped_column(String(20))  # 单位：kg/hours/km/bpm等
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # 备注
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 标签数组
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="health_records")


class WorkRecord(Base):
    """Work record model with task types."""
    __tablename__ = "work_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    task_type: Mapped[str] = mapped_column(String(50))  # 开发/会议/文档/学习/管理/协作
    task_name: Mapped[str] = mapped_column(String(200))
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    value_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 项目关联（可选）
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # high/medium/low
    status: Mapped[str] = mapped_column(String(20), default="completed")  # todo/in_progress/completed/cancelled
    start_time: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)  # 开始时间
    end_time: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)  # 结束时间
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 标签数组
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="work_records")


class LeisureRecord(Base):
    """Leisure record model with activity types."""
    __tablename__ = "leisure_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    activity_type: Mapped[str] = mapped_column(String(50))  # 运动/娱乐/户外/文化/放松
    activity: Mapped[str] = mapped_column(String(200))  # 具体活动描述
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 地点
    participants: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 参与人员
    enjoyment_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 享受度 1-5
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)  # 花费
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 标签数组
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="leisure_records")


class TimeLog(Base):
    """Time log model."""
    __tablename__ = "time_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP)
    end_time: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    activity: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="time_logs")


class LearningRecord(Base):
    """Learning record model."""
    __tablename__ = "learning_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    learning_type: Mapped[str] = mapped_column(String(50))  # 阅读/课程/技能/认证/实践
    title: Mapped[str] = mapped_column(String(200))  # 学习内容标题
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 进度百分比 0-100
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 来源：书籍/视频/文章/课程/实践
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 评分 1-5
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 标签数组
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="learning_records")


class SocialRecord(Base):
    """Social record model."""
    __tablename__ = "social_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    social_type: Mapped[str] = mapped_column(String(50))  # 家人/朋友/同事/网络
    participants: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 参与人员
    relationship_type: Mapped[str] = mapped_column(String(50))  # 关系类型：家人/朋友/同事/网络
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    activity: Mapped[str] = mapped_column(String(200))  # 活动内容
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 地点
    enjoyment_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 享受度 1-5
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)  # 花费
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 标签数组
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="social_records")


class Goal(Base):
    """Goal model."""
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    goal_type: Mapped[str] = mapped_column(String(50))  # health/finance/learning/work/life
    title: Mapped[str] = mapped_column(String(200))  # 目标标题
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # 详细描述
    target_value: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # 目标值
    current_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # 当前进度值
    unit: Mapped[str] = mapped_column(String(20))  # 单位
    start_date: Mapped[date] = mapped_column(Date)  # 开始日期
    target_date: Mapped[date] = mapped_column(Date)  # 目标日期
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/completed/paused/cancelled
    frequency: Mapped[str | None] = mapped_column(String(20), nullable=True)  # daily/weekly/monthly/one_time
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 标签数组
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="goals")
    progress_records: Mapped[list["GoalProgress"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )


class GoalProgress(Base):
    """Goal progress record model."""
    __tablename__ = "goal_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_id: Mapped[int] = mapped_column(Integer, ForeignKey("goals.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # 进度值
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    goal: Mapped["Goal"] = relationship(back_populates="progress_records")
    user: Mapped["User"] = relationship(back_populates="goal_progress")
