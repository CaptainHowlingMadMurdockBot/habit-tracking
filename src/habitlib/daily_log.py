"""Daily log writer for habit tracking.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.habitlib.models import DailyLogConfig, Habit, JournalPrompt


class DailyLog:
    def __init__(self, config: DailyLogConfig):
        self.config = config

    def is_enabled(self) -> bool:
        return self.config.enabled

    def path_for_date(self, date_str: str | None = None) -> Path:
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        path_str = self.config.path.replace("{date}", date_str)
        return Path(path_str)

    def log_habit(self, habit: Habit, time_of_day: str) -> str:
        if not self.is_enabled():
            return ""
        entry = f"- [x] {habit.emoji} {habit.behavior} ({time_of_day})"
        path = self.path_for_date()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{entry}\n")
        return entry

    def log_journal(self, prompt: JournalPrompt, response: str) -> str:
        entry = f"**{prompt.label}:** {response}"
        path = self.path_for_date()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{entry}\n")
        return entry

    def read_today(self) -> str:
        path = self.path_for_date()
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def has_habit_emoji(self, emoji: str) -> bool:
        content = self.read_today()
        return emoji in content
