"""AI text parser for natural language input."""
from datetime import date
from pathlib import Path
from typing import Dict, Any

from src.ai.providers import AIProviderFactory
from src.config import settings


class TextParser:
    """Parse natural language text into structured data using AI."""

    def __init__(self):
        """Initialize the parser with configured AI provider."""
        self.ai = AIProviderFactory.create(
            provider_type=settings.ai_provider,
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url,
            model=settings.ai_model,
        )
        self.prompts_dir = settings.prompts_dir

    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt template from file."""
        prompt_path = self.prompts_dir / prompt_name
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")

    def _format_date(self, date_obj: date) -> str:
        """Format date as YYYY-MM-DD."""
        return date_obj.strftime("%Y-%m-%d")

    def parse_finance(self, text: str, record_date: date | None = None) -> Dict[str, Any]:
        """
        Parse finance-related text.

        Args:
            text: Natural language text describing a finance record
            record_date: Date to use (defaults to today)

        Returns:
            Parsed finance data as dictionary
        """
        if record_date is None:
            record_date = date.today()

        prompt = self._load_prompt("parse_finance.txt")
        formatted_prompt = prompt.format(text=text, today=self._format_date(record_date))

        return self.ai.parse(formatted_prompt, context={})

    def parse_health(self, text: str, record_date: date | None = None) -> Dict[str, Any]:
        """
        Parse health-related text.

        Args:
            text: Natural language text describing a health record
            record_date: Date to use (defaults to today)

        Returns:
            Parsed health data as dictionary
        """
        if record_date is None:
            record_date = date.today()

        prompt = self._load_prompt("parse_health.txt")
        formatted_prompt = prompt.format(text=text, today=self._format_date(record_date))

        return self.ai.parse(formatted_prompt, context={})

    def parse_work(self, text: str, record_date: date | None = None) -> Dict[str, Any]:
        """
        Parse work-related text.

        Args:
            text: Natural language text describing a work record
            record_date: Date to use (defaults to today)

        Returns:
            Parsed work data as dictionary
        """
        if record_date is None:
            record_date = date.today()

        prompt = self._load_prompt("parse_work.txt")
        formatted_prompt = prompt.format(text=text, today=self._format_date(record_date))

        return self.ai.parse(formatted_prompt, context={})

    def parse_leisure(self, text: str, record_date: date | None = None) -> Dict[str, Any]:
        """
        Parse leisure-related text.

        Args:
            text: Natural language text describing a leisure record
            record_date: Date to use (defaults to today)

        Returns:
            Parsed leisure data as dictionary
        """
        if record_date is None:
            record_date = date.today()

        prompt = self._load_prompt("parse_leisure.txt")
        formatted_prompt = prompt.format(text=text, today=self._format_date(record_date))

        return self.ai.parse(formatted_prompt, context={})
