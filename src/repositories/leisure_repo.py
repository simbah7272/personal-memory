"""Leisure record repository."""
from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.core.models import LeisureRecord
from src.repositories.base import BaseRepository


class LeisureRepository(BaseRepository[LeisureRecord]):
    """Repository for leisure records."""

    def __init__(self, db: Session):
        """Initialize repository."""
        super().__init__(LeisureRecord, db)

    def create(
        self,
        user_id: int,
        record_date: date,
        activity_type: str,
        activity: str,
        duration_hours: Decimal,
        location: str | None = None,
        participants: list | None = None,
        enjoyment_score: int | None = None,
        cost: Decimal | None = None,
        tags: list | None = None,
        notes: str | None = None,
        raw_text: str | None = None,
    ) -> LeisureRecord:
        """
        Create a leisure record.

        Args:
            user_id: User ID
            record_date: Record date
            activity_type: Activity type (运动/娱乐/户外/文化/放松)
            activity: Activity description
            duration_hours: Duration in hours
            location: Location
            participants: List of participants
            enjoyment_score: Enjoyment score (1-5)
            cost: Cost amount
            tags: Tags list
            notes: Additional notes
            raw_text: Original input text

        Returns:
            Created leisure record
        """
        db_obj = LeisureRecord(
            user_id=user_id,
            record_date=record_date,
            activity_type=activity_type,
            activity=activity,
            duration_hours=duration_hours,
            location=location,
            participants=participants,
            enjoyment_score=enjoyment_score,
            cost=cost,
            tags=tags,
            notes=notes,
            raw_text=raw_text,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[LeisureRecord]:
        """
        Get records within a date range.

        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of leisure records
        """
        query = (
            select(LeisureRecord)
            .where(
                and_(
                    LeisureRecord.user_id == user_id,
                    LeisureRecord.record_date >= start_date,
                    LeisureRecord.record_date <= end_date,
                )
            )
            .order_by(LeisureRecord.record_date.desc())
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_activity(
        self,
        user_id: int,
        activity: str,
        limit: int = 100,
    ) -> List[LeisureRecord]:
        """
        Get records by activity name.

        Args:
            user_id: User ID
            activity: Activity name (partial match)
            limit: Maximum records to return

        Returns:
            List of leisure records
        """
        query = (
            select(LeisureRecord)
            .where(
                and_(
                    LeisureRecord.user_id == user_id,
                    LeisureRecord.activity.contains(activity),
                )
            )
            .order_by(LeisureRecord.record_date.desc())
            .limit(limit)
        )
        result = self.db.execute(query)
        return list(result.scalars().all())
