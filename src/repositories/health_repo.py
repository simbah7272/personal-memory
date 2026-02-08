"""Health record repository."""
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.core.models import HealthRecord
from src.repositories.base import BaseRepository


class HealthRepository(BaseRepository[HealthRecord]):
    """Repository for health records."""

    def __init__(self, db: Session):
        """Initialize repository."""
        super().__init__(HealthRecord, db)

    def create(
        self,
        user_id: int,
        record_date: date,
        sleep_hours: Optional[float] = None,
        sleep_quality: Optional[str] = None,
        wake_time: Optional[datetime] = None,
        bed_time: Optional[datetime] = None,
        mood: Optional[str] = None,
        notes: Optional[str] = None,
        raw_text: Optional[str] = None,
    ) -> HealthRecord:
        """
        Create a health record.

        Args:
            user_id: User ID
            record_date: Record date
            sleep_hours: Hours of sleep
            sleep_quality: Sleep quality description
            wake_time: Wake up time
            bed_time: Bed time
            mood: Mood description
            notes: Additional notes
            raw_text: Original input text

        Returns:
            Created health record
        """
        db_obj = HealthRecord(
            user_id=user_id,
            record_date=record_date,
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            wake_time=wake_time,
            bed_time=bed_time,
            mood=mood,
            notes=notes,
            raw_text=raw_text,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_date(
        self,
        user_id: int,
        record_date: date,
    ) -> Optional[HealthRecord]:
        """
        Get record by date.

        Args:
            user_id: User ID
            record_date: Record date

        Returns:
            Health record or None
        """
        query = select(HealthRecord).where(
            and_(
                HealthRecord.user_id == user_id,
                HealthRecord.record_date == record_date,
            )
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[HealthRecord]:
        """
        Get records within a date range.

        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of health records
        """
        query = (
            select(HealthRecord)
            .where(
                and_(
                    HealthRecord.user_id == user_id,
                    HealthRecord.record_date >= start_date,
                    HealthRecord.record_date <= end_date,
                )
            )
            .order_by(HealthRecord.record_date.desc())
        )
        result = self.db.execute(query)
        return list(result.scalars().all())
