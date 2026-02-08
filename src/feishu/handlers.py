"""Feishu event handlers with smart intent recognition."""
import asyncio
import nest_asyncio  # Allow nested event loops
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.config import settings
from src.core.models import FinanceRecord, HealthRecord, WorkRecord, LeisureRecord
from src.core.database import get_db
from src.services.record_service import RecordService
from src.repositories.user_repo import UserRepository
from src.ai.parser import TextParser

# Apply nest_asyncio patch globally
nest_asyncio.apply()


# Minimal MessageEvent for backward compatibility
@dataclass
class FeishuUser:
    """Feishu user information."""
    user_id: str


@dataclass
class MessageEvent:
    """Feishu message event (minimal version for backward compatibility)."""
    sender: FeishuUser
    content: str


# Query intent keywords
QUERY_KEYWORDS = [
    "查询", "看看", "显示", "统计", "多少", "总计", "一共",
    "报告", "汇总", "明细", "记录", "花了", "花费", "支出",
    "收入", "睡眠", "工作", "休闲", "运动",
]

# Record type keywords
RECORD_TYPE_KEYWORDS = {
    "finance": ["花了", "花费", "支出", "收入", "赚", "买", "支付", "付款"],
    "health": ["睡眠", "睡了", "睡觉", "心情", "健康", "运动", "锻炼"],
    "work": ["工作", "完成", "开发", "写", "修复", "任务"],
    "leisure": ["玩", "看", "听", "游戏", "电影", "音乐", "阅读"],
}


class FeishuEventHandler:
    """Handler for Feishu events."""

    def __init__(self, db: Session):
        """
        Initialize handler.

        Args:
            db: Database session
        """
        self.db = db
        self.parser = TextParser()
        self.user_repo = UserRepository(db)

    def handle_message_by_text(self, sender_id: str, text: str) -> str:
        """
        Handle text message (SDK-compatible entry point).

        This is the main entry point for SDK events.
        It extracts user and delegates to the appropriate handler.

        Args:
            sender_id: Feishu user ID
            text: Message text

        Returns:
            Response message
        """
        print("=" * 60, flush=True)
        print(f"📨 [1/6] 收到消息", flush=True)
        print(f"  发送者 ID: {sender_id}", flush=True)
        print(f"  消息内容: {text}", flush=True)
        print("=" * 60, flush=True)

        # Get or create user
        print(f"🔍 [2/6] 查询/创建用户...", flush=True)
        user = self.user_repo.get_or_create_by_feishu(sender_id)
        print(f"  ✓ 用户 ID: {user.id}", flush=True)
        print(f"  ✓ 用户名: {user.username}", flush=True)

        # Create service instance
        service = RecordService(self.db, user.id)

        # Helper to run async code (works with nest_asyncio)
        def run_async(coro):
            try:
                loop = asyncio.get_running_loop()
                return loop.run_until_complete(coro)
            except RuntimeError:
                return asyncio.run(coro)

        # Smart intent recognition (reuse existing logic)
        print(f"🎯 [3/6] 意图识别...", flush=True)

        if text.startswith("/"):
            print(f"  → 识别为: 命令 (以 / 开头)", flush=True)
            response = run_async(self.handle_command_by_service(service, text))
        elif self._is_query_intent(text):
            print(f"  → 识别为: 查询 (包含查询关键词)", flush=True)
            response = run_async(self.handle_query_by_service(service, text))
        else:
            print(f"  → 识别为: 记录 (默认)", flush=True)
            response = run_async(self.handle_record_by_service(service, text))

        print(f"📤 [6/6] 准备发送回复", flush=True)
        print(f"  回复内容: {response}", flush=True)
        print("=" * 60, flush=True)

        return response

    async def handle_message(self, event: MessageEvent) -> str:
        """
        Handle message event with smart intent recognition.

        Args:
            event: Message event

        Returns:
            Response message
        """
        content = event.content
        if not content:
            return "❓ 没有收到消息内容"

        # 1. Check if it's a command (starts with /)
        if content.startswith("/"):
            return await self.handle_command(event, content)

        # 2. Check if it's a query intent (contains query keywords)
        if self._is_query_intent(content):
            return await self.handle_query(event, content)

        # 3. Otherwise, treat as adding a record
        return await self.handle_record(event, content)

    def _is_query_intent(self, text: str) -> bool:
        """
        Check if text indicates a query intent.

        Args:
            text: Input text

        Returns:
            True if query intent detected
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in QUERY_KEYWORDS)

    async def handle_command_by_service(self, service: RecordService, command: str) -> str:
        """
        Handle traditional commands (with service).

        Args:
            service: RecordService instance
            command: Command string

        Returns:
            Response message
        """
        user_id = service.user_id

        # Parse command
        parts = command.strip().split()
        cmd = parts[0].lower() if parts else ""

        print(f"  → 命令类型: {cmd}", flush=True)
        print(f"📋 [4/6] 执行命令...", flush=True)

        if cmd == "/help":
            result = self._get_help_message()
            print(f"  ✓ 帮助信息已生成", flush=True)
            return result
        elif cmd == "/daily":
            print(f"  → 生成今日报告...", flush=True)
            result = await self._generate_daily_report(user_id)
            print(f"  ✓ 报告生成完成", flush=True)
            return result
        elif cmd == "/weekly":
            print(f"  → 生成本周报告...", flush=True)
            result = await self._generate_weekly_report(user_id)
            print(f"  ✓ 报告生成完成", flush=True)
            return result
        elif cmd == "/monthly":
            print(f"  → 生成本月报告...", flush=True)
            result = await self._generate_monthly_report(user_id)
            print(f"  ✓ 报告生成完成", flush=True)
            return result
        elif cmd == "/list":
            print(f"  → 列出最近记录...", flush=True)
            result = await self._list_recent_records(user_id, parts[1:] if len(parts) > 1 else [])
            print(f"  ✓ 列表生成完成", flush=True)
            return result
        else:
            print(f"  ✗ 未知命令: {cmd}", flush=True)
            return f"❓ 未知命令: {cmd}\n\n发送 /help 查看可用命令"

    async def handle_command(self, event: MessageEvent, command: str) -> str:
        """
        Handle traditional commands (legacy, for backward compatibility).

        Args:
            event: Message event
            command: Command string

        Returns:
            Response message
        """
        user = self.user_repo.get_or_create_by_feishu(event.sender.user_id)
        service = RecordService(self.db, user.id)
        return await self.handle_command_by_service(service, command)

    async def handle_query_by_service(self, service: RecordService, query: str) -> str:
        """
        Handle AI-powered smart query (with service).

        Args:
            service: RecordService instance
            query: Query text

        Returns:
            Query result
        """
        user_id = service.user_id
        print(f"🔍 [4/6] 解析查询意图...", flush=True)

        # Parse query using AI
        try:
            parsed = self._parse_query_intent(query)
            print(f"  → 查询解析结果:", flush=True)
            print(f"    - 记录类型: {parsed.get('record_type') or '全部'}", flush=True)
            print(f"    - 时间范围: {parsed.get('start_date')} 至 {parsed.get('end_date')}", flush=True)
            print(f"    - 查询类型: {parsed.get('query_type')}", flush=True)
            print(f"    - 分类: {parsed.get('category') or '不限'}", flush=True)
        except Exception as e:
            print(f"  ✗ 查询解析失败: {e}", flush=True)
            return f"❌ 查询解析失败: {str(e)}\n\n请尝试用更简单的方式描述，例如：\n• 查询本周花费\n• 今天的工作记录"

        print(f"📊 [5/6] 执行数据库查询...", flush=True)
        # Execute query based on parsed intent
        result = await self._execute_query(user_id, parsed)
        print(f"  ✓ 查询完成，结果长度: {len(result)} 字符", flush=True)
        return result

    async def handle_query(self, event: MessageEvent, query: str) -> str:
        """
        Handle AI-powered smart query (legacy, for backward compatibility).

        Args:
            event: Message event
            query: Query text

        Returns:
            Query result
        """
        user = self.user_repo.get_or_create_by_feishu(event.sender.user_id)
        service = RecordService(self.db, user.id)
        return await self.handle_query_by_service(service, query)

    def _parse_query_intent(self, query: str) -> dict[str, Any]:
        """
        Parse query intent using AI.

        Args:
            query: Query text

        Returns:
            Parsed query intent
        """
        # Simple rule-based parsing (can be enhanced with AI)
        today = date.today()
        parsed = {
            "record_type": None,
            "start_date": None,
            "end_date": None,
            "category": None,
            "query_type": "list",  # list, sum, avg, count
        }

        # Detect record type
        for record_type, keywords in RECORD_TYPE_KEYWORDS.items():
            if any(kw in query for kw in keywords):
                parsed["record_type"] = record_type
                break

        # Detect time range
        if "今天" in query:
            parsed["start_date"] = today
            parsed["end_date"] = today
        elif "昨天" in query:
            yesterday = today - timedelta(days=1)
            parsed["start_date"] = yesterday
            parsed["end_date"] = yesterday
        elif "本周" in query:
            start_of_week = today - timedelta(days=today.weekday())
            parsed["start_date"] = start_of_week
            parsed["end_date"] = today
        elif "上周" in query:
            start_of_week = today - timedelta(days=today.weekday() + 7)
            end_of_week = start_of_week + timedelta(days=6)
            parsed["start_date"] = start_of_week
            parsed["end_date"] = end_of_week
        elif "本月" in query:
            start_of_month = today.replace(day=1)
            parsed["start_date"] = start_of_month
            parsed["end_date"] = today
        elif "上月" in query:
            first_day = today.replace(day=1)
            last_month_end = first_day - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            parsed["start_date"] = last_month_start
            parsed["end_date"] = last_month_end

        # Detect query type
        if any(kw in query for kw in ["总计", "一共", "总共", "总和"]):
            parsed["query_type"] = "sum"
        elif any(kw in query for kw in ["平均", "均值"]):
            parsed["query_type"] = "avg"
        elif any(kw in query for kw in ["多少", "数量", "几条"]):
            parsed["query_type"] = "count"

        # Detect category for finance
        if parsed["record_type"] == "finance":
            categories = ["餐饮", "交通", "购物", "娱乐", "居住", "医疗", "教育", "其他"]
            for cat in categories:
                if cat in query:
                    parsed["category"] = cat
                    break

        return parsed

    async def _execute_query(self, user_id: int, parsed: dict[str, Any]) -> str:
        """
        Execute parsed query.

        Args:
            user_id: User ID
            parsed: Parsed query intent

        Returns:
            Query result
        """
        record_type = parsed.get("record_type")
        start_date = parsed.get("start_date")
        end_date = parsed.get("end_date")
        category = parsed.get("category")
        query_type = parsed.get("query_type", "list")

        # If no record type detected, show all types
        if not record_type:
            return await self._generate_multi_type_report(user_id, start_date, end_date)

        # Execute query by type
        if record_type == "finance":
            return await self._query_finance(user_id, start_date, end_date, category, query_type)
        elif record_type == "health":
            return await self._query_health(user_id, start_date, end_date, query_type)
        elif record_type == "work":
            return await self._query_work(user_id, start_date, end_date, query_type)
        elif record_type == "leisure":
            return await self._query_leisure(user_id, start_date, end_date, query_type)
        else:
            return "❓ 无法识别查询类型"

    async def _query_finance(
        self,
        user_id: int,
        start_date: date | None,
        end_date: date | None,
        category: str | None,
        query_type: str,
    ) -> str:
        """Query finance records."""
        from src.repositories.finance_repo import FinanceRepository

        repo = FinanceRepository(self.db)

        if query_type == "sum":
            if start_date and end_date:
                records = repo.get_by_date_range(user_id, start_date, end_date)
            else:
                records = repo.get_all(user_id, limit=1000)

            total_expense = sum(r.amount for r in records if r.type == "expense")
            total_income = sum(r.amount for r in records if r.type == "income")

            date_range = self._format_date_range(start_date, end_date)
            result = f"💸 财务统计 {date_range}\n\n"
            result += f"支出: ¥{total_expense:.2f}\n"
            result += f"收入: ¥{total_income:.2f}\n"
            result += f"结余: ¥{total_income - total_expense:.2f}"

            return result
        else:
            # List records
            if start_date and end_date:
                records = repo.get_by_date_range(user_id, start_date, end_date)
            else:
                records = repo.get_all(user_id, limit=20)

            if not records:
                return "📊 没有找到财务记录"

            result = "💸 财务记录\n\n"
            for r in records[:10]:
                icon = "💰" if r.type == "income" else "💸"
                result += f"{icon} {r.record_date} {r.description or r.category or ''} ¥{r.amount}\n"

            return result

    async def _query_health(
        self,
        user_id: int,
        start_date: date | None,
        end_date: date | None,
        query_type: str,
    ) -> str:
        """Query health records."""
        from src.repositories.health_repo import HealthRepository

        repo = HealthRepository(self.db)

        if start_date and end_date:
            records = [
                r for r in repo.get_all(user_id, limit=1000)
                if start_date <= r.record_date <= end_date
            ]
        else:
            records = repo.get_all(user_id, limit=7)

        if not records:
            return "😴 没有找到健康记录"

        result = "😴 健康记录\n\n"
        for r in records[:7]:
            sleep_info = f"{r.sleep_hours}h" if r.sleep_hours else "N/A"
            result += f"📅 {r.record_date} | 😴 {sleep_info} | {r.sleep_quality or 'N/A'}\n"

        return result

    async def _query_work(
        self,
        user_id: int,
        start_date: date | None,
        end_date: date | None,
        query_type: str,
    ) -> str:
        """Query work records."""
        from src.repositories.work_repo import WorkRepository

        repo = WorkRepository(self.db)

        if start_date and end_date:
            records = [
                r for r in repo.get_all(user_id, limit=1000)
                if start_date <= r.record_date <= end_date
            ]
        else:
            records = repo.get_all(user_id, limit=10)

        if not records:
            return "💼 没有找到工作记录"

        total_hours = sum(r.duration_hours for r in records)

        result = "💼 工作记录\n\n"
        for r in records[:10]:
            result += f"📅 {r.record_date} | ⏱ {r.duration_hours}h | {r.task_name}\n"

        result += f"\n总计: {total_hours}h"

        return result

    async def _query_leisure(
        self,
        user_id: int,
        start_date: date | None,
        end_date: date | None,
        query_type: str,
    ) -> str:
        """Query leisure records."""
        from src.repositories.leisure_repo import LeisureRepository

        repo = LeisureRepository(self.db)

        if start_date and end_date:
            records = [
                r for r in repo.get_all(user_id, limit=1000)
                if start_date <= r.record_date <= end_date
            ]
        else:
            records = repo.get_all(user_id, limit=10)

        if not records:
            return "🎮 没有找到休闲记录"

        total_hours = sum(r.duration_hours for r in records)

        result = "🎮 休闲记录\n\n"
        for r in records[:10]:
            result += f"📅 {r.record_date} | ⏱ {r.duration_hours}h | {r.activity}\n"

        result += f"\n总计: {total_hours}h"

        return result

    async def _generate_multi_type_report(
        self,
        user_id: int,
        start_date: date | None,
        end_date: date | None,
    ) -> str:
        """Generate report for all record types."""
        date_range = self._format_date_range(start_date, end_date)
        result = f"📊 数据统计 {date_range}\n\n"

        # Add summaries from each type
        finance_result = await self._query_finance(user_id, start_date, end_date, None, "sum")
        if not finance_result.startswith("❌"):
            result += finance_result + "\n\n"

        work_result = await self._query_work(user_id, start_date, end_date, "list")
        if not work_result.startswith("❌"):
            # Extract total hours
            lines = work_result.split("\n")
            for line in lines:
                if "总计" in line:
                    result += f"💼 {line}\n"
                    break

        return result

    def _format_date_range(self, start_date: date | None, end_date: date | None) -> str:
        """Format date range for display."""
        if start_date and end_date:
            if start_date == end_date:
                return f"({start_date})"
            return f"({start_date} 至 {end_date})"
        return ""

    async def handle_record_by_service(self, service: RecordService, text: str) -> str:
        """
        Handle adding a new record (with service).

        Args:
            service: RecordService instance
            text: Record text

        Returns:
            Confirmation message
        """
        print(f"🤖 [4/6] AI 解析开始...", flush=True)

        # Detect record type by keywords
        record_type = self._detect_record_type(text)
        print(f"  → 检测到记录类型: {record_type or '未知'}", flush=True)

        try:
            if record_type == "finance":
                print(f"  → 调用 AI 解析财务记录...", flush=True)
                record = await service.add_finance_from_text(text)
                icon = "💰" if record.type == "income" else "💸"
                result = f"✅ 已添加：{icon} {record.description or record.category or ''} ¥{record.amount}"
                print(f"  ✓ AI 解析成功:", flush=True)
                print(f"    - 类型: {record.type}", flush=True)
                print(f"    - 金额: ¥{record.amount}", flush=True)
                print(f"    - 描述: {record.description or record.category or ''}", flush=True)
                return result

            elif record_type == "health":
                print(f"  → 调用 AI 解析健康记录...", flush=True)
                record = await service.add_health_from_text(text)
                sleep_info = f"{record.sleep_hours}h" if record.sleep_hours else "N/A"
                result = f"✅ 已添加：😴 睡眠 {sleep_info} - {record.sleep_quality or 'N/A'}"
                print(f"  ✓ AI 解析成功:", flush=True)
                print(f"    - 睡眠时长: {sleep_info}", flush=True)
                print(f"    - 睡眠质量: {record.sleep_quality or 'N/A'}", flush=True)
                return result

            elif record_type == "work":
                print(f"  → 调用 AI 解析工作记录...", flush=True)
                record = await service.add_work_from_text(text)
                result = f"✅ 已添加：💼 {record.task_name} ({record.duration_hours}h)"
                print(f"  ✓ AI 解析成功:", flush=True)
                print(f"    - 任务: {record.task_name}", flush=True)
                print(f"    - 时长: {record.duration_hours}h", flush=True)
                return result

            elif record_type == "leisure":
                print(f"  → 调用 AI 解析休闲记录...", flush=True)
                record = await service.add_leisure_from_text(text)
                result = f"✅ 已添加：🎮 {record.activity} ({record.duration_hours}h)"
                print(f"  ✓ AI 解析成功:", flush=True)
                print(f"    - 活动: {record.activity}", flush=True)
                print(f"    - 时长: {record.duration_hours}h", flush=True)
                return result

            else:
                print(f"  ✗ 无法识别记录类型", flush=True)
                return "❓ 无法识别记录类型\n\n请尝试：\n• 今天花了50块买午饭\n• 昨晚睡了8小时\n• 今天工作了4小时完成开发\n• 看了2小时电影"

        except Exception as e:
            print(f"  ✗ AI 解析失败: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return f"❌ 添加失败: {str(e)}"

    async def handle_record(self, event: MessageEvent, text: str) -> str:
        """
        Handle adding a new record (with service).

        Args:
            service: RecordService instance
            text: Record text

        Returns:
            Confirmation message
        """
        # Detect record type by keywords
        record_type = self._detect_record_type(text)

        try:
            if record_type == "finance":
                record = await service.add_finance_from_text(text)
                icon = "💰" if record.type == "income" else "💸"
                return f"✅ 已添加：{icon} {record.description or record.category or ''} ¥{record.amount}"

            elif record_type == "health":
                record = await service.add_health_from_text(text)
                sleep_info = f"{record.sleep_hours}h" if record.sleep_hours else "N/A"
                return f"✅ 已添加：😴 睡眠 {sleep_info} - {record.sleep_quality or 'N/A'}"

            elif record_type == "work":
                record = await service.add_work_from_text(text)
                return f"✅ 已添加：💼 {record.task_name} ({record.duration_hours}h)"

            elif record_type == "leisure":
                record = await service.add_leisure_from_text(text)
                return f"✅ 已添加：🎮 {record.activity} ({record.duration_hours}h)"

            else:
                return "❓ 无法识别记录类型\n\n请尝试：\n• 今天花了50块买午饭\n• 昨晚睡了8小时\n• 今天工作了4小时完成开发\n• 看了2小时电影"

        except Exception as e:
            return f"❌ 添加失败: {str(e)}"

    async def handle_record(self, event: MessageEvent, text: str) -> str:
        """
        Handle adding a new record (legacy, for backward compatibility).

        Args:
            event: Message event
            text: Record text

        Returns:
            Confirmation message
        """
        user = self.user_repo.get_or_create_by_feishu(event.sender.user_id)
        service = RecordService(self.db, user.id)
        return await self.handle_record_by_service(service, text)

    def _detect_record_type(self, text: str) -> str | None:
        """
        Detect record type by keywords.

        Args:
            text: Input text

        Returns:
            Record type or None
        """
        for record_type, keywords in RECORD_TYPE_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return record_type
        return None

    def _get_help_message(self) -> str:
        """Get help message."""
        return """🤖 个人记忆助手

📝 记录数据（直接输入）：
• 今天花了50块买午饭
• 昨晚睡了8小时
• 今天工作了4小时
• 看了2小时电影

🔍 查询数据（自然语言）：
• 查询本周花费
• 看看今天的工作记录
• 昨天睡了多少小时
• 上个月在餐饮上花了多少钱

📋 快捷命令：
• /daily - 今日报告
• /weekly - 本周报告
• /monthly - 本月报告
• /list - 最近记录
• /help - 帮助信息"""

    async def _generate_daily_report(self, user_id: int) -> str:
        """Generate daily report."""
        today = date.today()
        return await self._execute_query(user_id, {
            "record_type": None,
            "start_date": today,
            "end_date": today,
            "query_type": "list",
        })

    async def _generate_weekly_report(self, user_id: int) -> str:
        """Generate weekly report."""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        return await self._execute_query(user_id, {
            "record_type": None,
            "start_date": start_of_week,
            "end_date": today,
            "query_type": "list",
        })

    async def _generate_monthly_report(self, user_id: int) -> str:
        """Generate monthly report."""
        today = date.today()
        start_of_month = today.replace(day=1)
        return await self._execute_query(user_id, {
            "record_type": None,
            "start_date": start_of_month,
            "end_date": today,
            "query_type": "list",
        })

    async def _list_recent_records(self, user_id: int, args: list[str]) -> str:
        """List recent records."""
        record_type = args[0] if args else None

        if record_type == "finance":
            return await self._query_finance(user_id, None, None, None, "list")
        elif record_type == "health":
            return await self._query_health(user_id, None, None, "list")
        elif record_type == "work":
            return await self._query_work(user_id, None, None, "list")
        elif record_type == "leisure":
            return await self._query_leisure(user_id, None, None, "list")
        else:
            return await self._generate_multi_type_report(user_id, None, None)
