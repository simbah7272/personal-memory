"""Finance record repository."""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from src.core.models import FinanceRecord
from src.repositories.base import BaseRepository


class FinanceRepository(BaseRepository[FinanceRecord]):
    """Repository for finance records."""

    def __init__(self, db: Session):
        """Initialize repository."""
        super().__init__(FinanceRecord, db)

    def create(
        self,
        user_id: int,
        type: str,
        amount: Decimal,
        record_date: date,
        category: str | None = None,
        description: str | None = None,
        raw_text: str | None = None,
    ) -> FinanceRecord:
        """
        Create a finance record.

        Args:
            user_id: User ID
            type: Record type (income/expense)
            amount: Amount
            record_date: Record date
            category: Category
            description: Description
            raw_text: Original input text

        Returns:
            Created finance record
        """
        db_obj = FinanceRecord(
            user_id=user_id,
            type=type,
            amount=amount,
            category=category,
            description=description,
            raw_text=raw_text,
            record_date=record_date,
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
    ) -> List[FinanceRecord]:
        """
        Get records within a date range.

        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of finance records
        """
        query = (
            select(FinanceRecord)
            .where(
                and_(
                    FinanceRecord.user_id == user_id,
                    FinanceRecord.record_date >= start_date,
                    FinanceRecord.record_date <= end_date,
                )
            )
            .order_by(FinanceRecord.record_date.desc())
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_type(
        self,
        user_id: int,
        type: str,
        limit: int = 100,
    ) -> List[FinanceRecord]:
        """
        Get records by type.

        Args:
            user_id: User ID
            type: Record type (income/expense)
            limit: Maximum records to return

        Returns:
            List of finance records
        """
        query = (
            select(FinanceRecord)
            .where(
                and_(
                    FinanceRecord.user_id == user_id,
                    FinanceRecord.type == type,
                )
            )
            .order_by(FinanceRecord.record_date.desc())
            .limit(limit)
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_category_summary(
        self,
        user_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> List[dict]:
        """
        Get summary by category.

        Args:
            user_id: User ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of category summaries
        """
        query = select(
            FinanceRecord.category,
            FinanceRecord.type,
            FinanceRecord.amount,
        ).where(FinanceRecord.user_id == user_id)

        if start_date:
            query = query.where(FinanceRecord.record_date >= start_date)
        if end_date:
            query = query.where(FinanceRecord.record_date <= end_date)

        result = self.db.execute(query)
        records = result.all()

        # Aggregate by category and type
        summary = {}
        for category, type_, amount in records:
            key = (category or "未分类", type_)
            if key not in summary:
                summary[key] = Decimal("0")
            summary[key] += amount

        return [
            {"category": cat, "type": type_, "total": float(amount)}
            for (cat, type_), amount in summary.items()
        ]
