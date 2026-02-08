"""Learning record repository."""
from typing import List, Optional
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.core.models import LearningRecord
from src.repositories.base import BaseRepository


class LearningRepository(BaseRepository[LearningRecord]):
    """Repository for learning records."""

    def __init__(self, db: Session):
        """
        Initialize learning repository.

        Args:
            db: Database session
        """
        super().__init__(LearningRecord, db)

    def get_by_date(
        self,
        user_id: int,
        record_date: date,
    ) -> List[LearningRecord]:
        """
        Get learning records by date.

        Args:
            user_id: User ID
            record_date: Record date

        Returns:
            List of learning records
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.record_date == record_date,
            )
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_type(
        self,
        user_id: int,
        learning_type: str,
        limit: int = 100,
    ) -> List[LearningRecord]:
        """
        Get learning records by type.

        Args:
            user_id: User ID
            learning_type: Learning type
            limit: Maximum number of records

        Returns:
            List of learning records
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.learning_type == learning_type,
            )
        ).order_by(self.model.record_date.desc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[LearningRecord]:
        """
        Get learning records within date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            List of learning records
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.record_date >= start_date,
                self.model.record_date <= end_date,
            )
        ).order_by(self.model.record_date.desc())

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_total_hours_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> float:
        """
        Get total learning hours within date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            Total learning hours
        """
        from sqlalchemy import func

        query = select(func.sum(self.model.duration_hours)).where(
            and_(
                self.model.user_id == user_id,
                self.model.record_date >= start_date,
                self.model.record_date <= end_date,
            )
        )

        result = self.db.execute(query)
        total = result.scalar()
        return float(total) if total else 0.0

    def get_stats_by_type(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        """
        Get learning statistics by type.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            List of stats with learning_type and total_hours
        """
        from sqlalchemy import func

        query = (
            select(
                self.model.learning_type,
                func.sum(self.model.duration_hours).label("total_hours"),
                func.count(self.model.id).label("count"),
            )
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.record_date >= start_date,
                    self.model.record_date <= end_date,
                )
            )
            .group_by(self.model.learning_type)
            .order_by(func.sum(self.model.duration_hours).desc())
        )

        result = self.db.execute(query)
        return [
            {"learning_type": row.learning_type, "total_hours": float(row.total_hours), "count": row.count}
            for row in result.all()
        ]
