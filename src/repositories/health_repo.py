"""Health record repository."""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from src.core.models import HealthRecord
from src.repositories.base import BaseRepository


class HealthRepository(BaseRepository[HealthRecord]):
    """Repository for health records with multi-indicator support."""

    def __init__(self, db: Session):
        """Initialize repository."""
        super().__init__(HealthRecord, db)

    def create(
        self,
        user_id: int,
        record_date: date,
        indicator_type: str,
        indicator_name: str,
        value: Decimal,
        unit: str,
        notes: Optional[str] = None,
        tags: Optional[list] = None,
        raw_text: Optional[str] = None,
    ) -> HealthRecord:
        """
        Create a health record.

        Args:
            user_id: User ID
            record_date: Record date
            indicator_type: Indicator type (sleep/exercise/diet/body/mental/medical)
            indicator_name: Specific indicator name
            value: Indicator value
            unit: Unit of measurement
            notes: Additional notes
            tags: Tags list
            raw_text: Original input text

        Returns:
            Created health record
        """
        db_obj = HealthRecord(
            user_id=user_id,
            record_date=record_date,
            indicator_type=indicator_type,
            indicator_name=indicator_name,
            value=value,
            unit=unit,
            notes=notes,
            tags=tags,
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
    ) -> List[HealthRecord]:
        """
        Get all records by date.

        Args:
            user_id: User ID
            record_date: Record date

        Returns:
            List of health records
        """
        query = select(HealthRecord).where(
            and_(
                HealthRecord.user_id == user_id,
                HealthRecord.record_date == record_date,
            )
        ).order_by(HealthRecord.created_at.desc())

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_indicator_type(
        self,
        user_id: int,
        indicator_type: str,
        limit: int = 100,
    ) -> List[HealthRecord]:
        """
        Get records by indicator type.

        Args:
            user_id: User ID
            indicator_type: Indicator type
            limit: Maximum records to return

        Returns:
            List of health records
        """
        query = (
            select(HealthRecord)
            .where(
                and_(
                    HealthRecord.user_id == user_id,
                    HealthRecord.indicator_type == indicator_type,
                )
            )
            .order_by(HealthRecord.record_date.desc())
            .limit(limit)
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_indicator_name(
        self,
        user_id: int,
        indicator_name: str,
        limit: int = 100,
    ) -> List[HealthRecord]:
        """
        Get records by indicator name.

        Args:
            user_id: User ID
            indicator_name: Indicator name
            limit: Maximum records to return

        Returns:
            List of health records
        """
        query = (
            select(HealthRecord)
            .where(
                and_(
                    HealthRecord.user_id == user_id,
                    HealthRecord.indicator_name == indicator_name,
                )
            )
            .order_by(HealthRecord.record_date.desc())
            .limit(limit)
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
        indicator_type: Optional[str] = None,
    ) -> List[HealthRecord]:
        """
        Get records within a date range.

        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            indicator_type: Optional indicator type filter

        Returns:
            List of health records
        """
        conditions = [
            HealthRecord.user_id == user_id,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date,
        ]

        if indicator_type:
            conditions.append(HealthRecord.indicator_type == indicator_type)

        query = (
            select(HealthRecord)
            .where(and_(*conditions))
            .order_by(HealthRecord.record_date.desc())
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_latest_by_indicator_type(
        self,
        user_id: int,
        indicator_type: str,
    ) -> Optional[HealthRecord]:
        """
        Get latest record for a specific indicator type.

        Args:
            user_id: User ID
            indicator_type: Indicator type

        Returns:
            Latest health record or None
        """
        query = (
            select(HealthRecord)
            .where(
                and_(
                    HealthRecord.user_id == user_id,
                    HealthRecord.indicator_type == indicator_type,
                )
            )
            .order_by(HealthRecord.record_date.desc())
            .limit(1)
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_indicator_summary(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        """
        Get summary by indicator type.

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date

        Returns:
            List of indicator summaries
        """
        query = (
            select(
                HealthRecord.indicator_type,
                HealthRecord.indicator_name,
                func.avg(HealthRecord.value).label("avg_value"),
                func.min(HealthRecord.value).label("min_value"),
                func.max(HealthRecord.value).label("max_value"),
                func.count(HealthRecord.id).label("count"),
            )
            .where(
                and_(
                    HealthRecord.user_id == user_id,
                    HealthRecord.record_date >= start_date,
                    HealthRecord.record_date <= end_date,
                )
            )
            .group_by(
                HealthRecord.indicator_type,
                HealthRecord.indicator_name,
            )
            .order_by(HealthRecord.indicator_type)
        )

        result = self.db.execute(query)
        return [
            {
                "indicator_type": row.indicator_type,
                "indicator_name": row.indicator_name,
                "avg_value": float(row.avg_value) if row.avg_value else 0.0,
                "min_value": float(row.min_value) if row.min_value else 0.0,
                "max_value": float(row.max_value) if row.max_value else 0.0,
                "count": row.count,
            }
            for row in result.all()
        ]
