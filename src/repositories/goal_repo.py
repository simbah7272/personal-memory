"""Goal and goal progress repositories."""
from typing import List, Optional
from datetime import date

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from src.core.models import Goal, GoalProgress
from src.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    """Repository for goals."""

    def __init__(self, db: Session):
        """
        Initialize goal repository.

        Args:
            db: Database session
        """
        super().__init__(Goal, db)

    def get_by_type(
        self,
        user_id: int,
        goal_type: str,
        limit: int = 100,
    ) -> List[Goal]:
        """
        Get goals by type.

        Args:
            user_id: User ID
            goal_type: Goal type
            limit: Maximum number of records

        Returns:
            List of goals
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.goal_type == goal_type,
            )
        ).order_by(self.model.created_at.desc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_status(
        self,
        user_id: int,
        status: str,
        limit: int = 100,
    ) -> List[Goal]:
        """
        Get goals by status.

        Args:
            user_id: User ID
            status: Goal status
            limit: Maximum number of records

        Returns:
            List of goals
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status == status,
            )
        ).order_by(self.model.target_date.asc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_active_goals(
        self,
        user_id: int,
        limit: int = 100,
    ) -> List[Goal]:
        """
        Get active goals.

        Args:
            user_id: User ID
            limit: Maximum number of records

        Returns:
            List of active goals
        """
        return self.get_by_status(user_id, "active", limit)

    def get_goals_due_soon(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 10,
    ) -> List[Goal]:
        """
        Get goals due within specified days.

        Args:
            user_id: User ID
            days: Number of days
            limit: Maximum number of records

        Returns:
            List of goals due soon
        """
        from datetime import timedelta

        due_date = date.today() + timedelta(days=days)

        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status == "active",
                self.model.target_date <= due_date,
            )
        ).order_by(self.model.target_date.asc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def update_current_value(
        self,
        goal_id: int,
        value: float,
    ) -> Optional[Goal]:
        """
        Update goal current value.

        Args:
            goal_id: Goal ID
            value: New current value

        Returns:
            Updated goal or None if not found
        """
        goal = self.get_by_id(goal_id)
        if goal:
            goal.current_value = value

            # Auto-complete goal if target reached
            if value >= goal.target_value:
                goal.status = "completed"

            self.db.commit()
            self.db.refresh(goal)
        return goal

    def calculate_progress_percentage(self, goal_id: int) -> float:
        """
        Calculate goal progress percentage.

        Args:
            goal_id: Goal ID

        Returns:
            Progress percentage (0-100)
        """
        goal = self.get_by_id(goal_id)
        if not goal or goal.target_value == 0:
            return 0.0

        return min(100.0, float(goal.current_value / goal.target_value * 100))


class GoalProgressRepository(BaseRepository[GoalProgress]):
    """Repository for goal progress records."""

    def __init__(self, db: Session):
        """
        Initialize goal progress repository.

        Args:
            db: Database session
        """
        super().__init__(GoalProgress, db)

    def get_by_goal(
        self,
        goal_id: int,
        limit: int = 100,
    ) -> List[GoalProgress]:
        """
        Get progress records for a goal.

        Args:
            goal_id: Goal ID
            limit: Maximum number of records

        Returns:
            List of progress records
        """
        query = select(self.model).where(
            self.model.goal_id == goal_id
        ).order_by(self.model.record_date.desc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_date_range(
        self,
        goal_id: int,
        start_date: date,
        end_date: date,
    ) -> List[GoalProgress]:
        """
        Get progress records within date range.

        Args:
            goal_id: Goal ID
            start_date: Start date
            end_date: End date

        Returns:
            List of progress records
        """
        query = select(self.model).where(
            and_(
                self.model.goal_id == goal_id,
                self.model.record_date >= start_date,
                self.model.record_date <= end_date,
            )
        ).order_by(self.model.record_date.asc())

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_latest_progress(
        self,
        goal_id: int,
    ) -> Optional[GoalProgress]:
        """
        Get latest progress record for a goal.

        Args:
            goal_id: Goal ID

        Returns:
            Latest progress record or None
        """
        query = select(self.model).where(
            self.model.goal_id == goal_id
        ).order_by(self.model.record_date.desc()).limit(1)

        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_total_progress_by_date_range(
        self,
        goal_id: int,
        start_date: date,
        end_date: date,
    ) -> float:
        """
        Get total progress within date range.

        Args:
            goal_id: Goal ID
            start_date: Start date
            end_date: End date

        Returns:
            Total progress value
        """
        query = select(func.sum(self.model.value)).where(
            and_(
                self.model.goal_id == goal_id,
                self.model.record_date >= start_date,
                self.model.record_date <= end_date,
            )
        )

        result = self.db.execute(query)
        total = result.scalar()
        return float(total) if total else 0.0

    def get_user_goal_progress(
        self,
        user_id: int,
        goal_id: int,
        limit: int = 100,
    ) -> List[GoalProgress]:
        """
        Get progress records for a user's goal.

        Args:
            user_id: User ID
            goal_id: Goal ID
            limit: Maximum number of records

        Returns:
            List of progress records
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.goal_id == goal_id,
            )
        ).order_by(self.model.record_date.desc()).limit(limit)

        result = self.db.execute(query)
        return list(result.scalars().all())
