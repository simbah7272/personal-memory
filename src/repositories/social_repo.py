"""Social record repository."""
from typing import List, Optional
from datetime import date

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from src.core.models import SocialRecord
from src.repositories.base import BaseRepository


class SocialRepository(BaseRepository[SocialRecord]):
    """Repository for social records."""

    def __init__(self, db: Session):
        """
        Initialize social repository.

        Args:
            db: Database session
        """
        super().__init__(SocialRecord, db)

    def get_by_date(
        self,
        user_id: int,
        record_date: date,
    ) -> List[SocialRecord]:
        """
        Get social records by date.

        Args:
            user_id: User ID
            record_date: Record date

        Returns:
            List of social records
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
        social_type: str,
        limit: int = 100,
    ) -> List[SocialRecord]:
        """
        Get social records by type.

        Args:
            user_id: User ID
            social_type: Social type
            limit: Maximum number of records

        Returns:
            List of social records
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.social_type == social_type,
            )
        ).order_by(self.model.record_date.desc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_relationship(
        self,
        user_id: int,
        relationship_type: str,
        limit: int = 100,
    ) -> List[SocialRecord]:
        """
        Get social records by relationship type.

        Args:
            user_id: User ID
            relationship_type: Relationship type
            limit: Maximum number of records

        Returns:
            List of social records
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.relationship_type == relationship_type,
            )
        ).order_by(self.model.record_date.desc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[SocialRecord]:
        """
        Get social records within date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            List of social records
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
        Get total social hours within date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            Total social hours
        """
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

    def get_total_cost_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> float:
        """
        Get total social cost within date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            Total social cost
        """
        query = select(func.sum(self.model.cost)).where(
            and_(
                self.model.user_id == user_id,
                self.model.record_date >= start_date,
                self.model.record_date <= end_date,
            )
        )

        result = self.db.execute(query)
        total = result.scalar()
        return float(total) if total else 0.0

    def get_stats_by_relationship(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        """
        Get social statistics by relationship type.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            List of stats with relationship, total_hours, total_cost, and count
        """
        query = (
            select(
                self.model.relationship_type,
                func.sum(self.model.duration_hours).label("total_hours"),
                func.sum(self.model.cost).label("total_cost"),
                func.count(self.model.id).label("count"),
            )
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.record_date >= start_date,
                    self.model.record_date <= end_date,
                )
            )
            .group_by(self.model.relationship_type)
            .order_by(func.sum(self.model.duration_hours).desc())
        )

        result = self.db.execute(query)
        return [
            {
                "relationship": row.relationship_type,
                "total_hours": float(row.total_hours) if row.total_hours else 0.0,
                "total_cost": float(row.total_cost) if row.total_cost else 0.0,
                "count": row.count,
            }
            for row in result.all()
        ]

    def get_average_enjoyment_score(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> float:
        """
        Get average enjoyment score within date range.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            Average enjoyment score
        """
        query = select(func.avg(self.model.enjoyment_score)).where(
            and_(
                self.model.user_id == user_id,
                self.model.record_date >= start_date,
                self.model.record_date <= end_date,
                self.model.enjoyment_score.isnot(None),
            )
        )

        result = self.db.execute(query)
        avg = result.scalar()
        return float(avg) if avg else 0.0
