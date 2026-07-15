import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from src.habitlib.models import DailyLogConfig, Habit, JournalPrompt
from src.habitlib.daily_log import DailyLog


def test_path_for_date_replaces_placeholder_today():
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "log_{date}.txt"
        config = DailyLogConfig(enabled=True, path=str(log_path))
        dl = DailyLog(config)
        result_path = dl.path_for_date()
        today_str = datetime.now().strftime("%Y-%m-%d")
        assert str(result_path) == str(Path(td) / f"log_{today_str}.txt")

def test_path_for_date_with_custom_date():
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "logs/{date}.log"
        config = DailyLogConfig(enabled=True, path=str(log_path))
        dl = DailyLog(config)

        custom_date = "2023-01-15"
        result_path = dl.path_for_date(custom_date)

        assert str(result_path) == str(Path(td) / "logs" / f"{custom_date}.log")

def test_log_habit_appends_to_file():
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "daily_{date}.log"
        config = DailyLogConfig(enabled=True, path=str(log_path))
        dl = DailyLog(config)

        habit = Habit(id="test", anchor="test", behavior="Read book", celebration="Good job!", emoji="📖", time_of_day="morning")
        time_of_day = "morning"
        expected_entry = f"- [x] {habit.emoji} {habit.behavior} ({time_of_day})"

        returned_entry = dl.log_habit(habit, time_of_day)
        assert returned_entry == expected_entry

        path = dl.path_for_date()
        assert path.exists()
        content = path.read_text()
        assert expected_entry in content

def test_log_journal_appends_to_file():
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "journal_{date}.md"
        config = DailyLogConfig(enabled=True, path=str(log_path))
        dl = DailyLog(config)

        prompt = JournalPrompt(id="gratitude", label="Gratitude", prompt="What are you grateful for?")
        response = "My family and a warm cup of coffee."
        expected_entry = f"**{prompt.label}:** {response}"

        returned_entry = dl.log_journal(prompt, response)
        assert returned_entry == expected_entry

        path = dl.path_for_date()
        assert path.exists()
        content = path.read_text()
        assert expected_entry in content

def test_creates_parent_directories_if_needed():
    with tempfile.TemporaryDirectory() as td:
        non_existent_dir = Path(td) / "a" / "b" / "c"
        log_path = non_existent_dir / "daily_{date}.log"
        config = DailyLogConfig(enabled=True, path=str(log_path))
        dl = DailyLog(config)

        habit = Habit(id="test", anchor="test", behavior="Test dir creation", celebration="Yay!", emoji="📁", time_of_day="any")
        dl.log_habit(habit, "any")

        assert non_existent_dir.exists()
        assert non_existent_dir.is_dir()

def test_read_today_returns_content():
    with tempfile.TemporaryDirectory() as td:
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_file_path_template = Path(td) / "daily_{date}.log"
        config = DailyLogConfig(enabled=True, path=str(log_file_path_template))
        dl = DailyLog(config)

        log_file_to_write = dl.path_for_date()
        log_file_to_write.parent.mkdir(parents=True, exist_ok=True)

        expected_content = "Test content line 1\nTest content line 2\n"
        with open(log_file_to_write, "w") as f:
            f.write(expected_content)

        read_content = dl.read_today()
        assert read_content == expected_content

def test_read_today_returns_empty_string_for_missing_file():
    with tempfile.TemporaryDirectory() as td:
        log_file_path_template = Path(td) / "daily_{date}.log"
        config = DailyLogConfig(enabled=True, path=str(log_file_path_template))
        dl = DailyLog(config)

        assert not dl.path_for_date().exists()

        read_content = dl.read_today()
        assert read_content == ""

def test_has_habit_emoji_returns_true_when_found():
    with tempfile.TemporaryDirectory() as td:
        log_file_path_template = Path(td) / "daily_{date}.log"
        config = DailyLogConfig(enabled=True, path=str(log_file_path_template))
        dl = DailyLog(config)

        emoji_to_find = "💪"
        content = f"- [x] {emoji_to_find} Workout\n- [x] 📖 Read Book\n"
        
        log_file_to_write = dl.path_for_date()
        log_file_to_write.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file_to_write, "w") as f:
            f.write(content)

        assert dl.has_habit_emoji(emoji_to_find) is True

def test_has_habit_emoji_returns_false_when_not_found():
    with tempfile.TemporaryDirectory() as td:
        log_file_path_template = Path(td) / "daily_{date}.log"
        config = DailyLogConfig(enabled=True, path=str(log_file_path_template))
        dl = DailyLog(config)

        emoji_to_find = "🧘"
        content = f"- [x] 💪 Workout\n- [x] 📖 Read Book\n"

        log_file_to_write = dl.path_for_date()
        log_file_to_write.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file_to_write, "w") as f:
            f.write(content)

        assert dl.has_habit_emoji(emoji_to_find) is False
