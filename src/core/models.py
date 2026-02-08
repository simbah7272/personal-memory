"""SQLAlchemy ORM models."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Integer, String, Text, Time, Numeric, TIMESTAMP, ForeignKey
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
    time_logs: Mapped[list["TimeLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class FinanceRecord(Base):
    """Finance record model."""
    __tablename__ = "finance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(10))  # 'income' | 'expense'
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    record_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="finance_records")


class HealthRecord(Base):
    """Health record model."""
    __tablename__ = "health_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    sleep_quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    wake_time: Mapped[datetime | None] = mapped_column(Time, nullable=True)
    bed_time: Mapped[datetime | None] = mapped_column(Time, nullable=True)
    mood: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="health_records")


class WorkRecord(Base):
    """Work record model."""
    __tablename__ = "work_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    task_name: Mapped[str] = mapped_column(String(200))
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    value_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="work_records")


class LeisureRecord(Base):
    """Leisure record model."""
    __tablename__ = "leisure_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    record_date: Mapped[date] = mapped_column(Date)
    activity: Mapped[str] = mapped_column(String(100))
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    enjoyment_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
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
