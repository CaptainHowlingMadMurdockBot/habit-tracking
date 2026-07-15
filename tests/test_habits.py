"""Tests for HabitStore YAML persistence using strict TDD.

The tests cover loading defaults, saving/loading round-trip, adding/removing habits,
and handling of duplicate IDs and missing files.
"""

import tempfile
from pathlib import Path

import pytest

from src.habitlib.models import Habit, CoachingConfig, HabitStoreConfig, Reminder, JournalPrompt, EnvironmentConfig, ValidationError
from src.habitlib.habits import HabitStore


def _default_store(tmp_path: Path) -> HabitStore:
    """Create a HabitStore pointing at a temporary file inside ``tmp_path``.
    The file does not exist initially.
    """
    return HabitStore(tmp_path / "habits.yaml")


def test_load_nonexistent_returns_defaults(tmp_path: Path):
    store = _default_store(tmp_path)
    cfg = store.load()
    assert isinstance(cfg, HabitStoreConfig)
    # defaults
    assert isinstance(cfg.coaching, CoachingConfig)
    assert cfg.coaching.style == "direct"
    assert cfg.habits == []


def test_load_empty_file_returns_defaults(tmp_path: Path):
    file_path = tmp_path / "empty.yaml"
    file_path.touch()
    store = HabitStore(file_path)
    cfg = store.load()
    assert isinstance(cfg, HabitStoreConfig)
    assert cfg.habits == []
    # coaching defaults
    assert cfg.coaching.style == "direct"


def test_save_and_reload_roundtrip(tmp_path: Path):
    store = _default_store(tmp_path)
    habit1 = Habit(
        id="h1",
        anchor="After coffee",
        behavior="Take vitamins",
        celebration="Yay",
        emoji="💊",
        time_of_day="morning",
    )
    cfg = HabitStoreConfig(
        coaching=CoachingConfig(style="warm", missed_day_policy="retry_once", schedule_time="07:30"),
        habits=[habit1],
        environment=EnvironmentConfig(),
        celebrations=["Congrats"],
        reminders=[
            Reminder(
                id="r1",
                schedule="08:00",
                cadence="daily",
                message="Reminder msg",
                habits=["h1"],
            )
        ],
        journal=[
            JournalPrompt(
                id="j1",
                label="Daily",
                prompt="How are you?",
            )
        ],
    )
    store.save(cfg)
    loaded = store.load()
    assert loaded.coaching.style == "warm"
    assert loaded.coaching.missed_day_policy == "retry_once"
    assert loaded.coaching.schedule_time == "07:30"
    assert len(loaded.habits) == 1
    assert loaded.habits[0] == habit1
    assert loaded.celebrations == ["Congrats"]
    assert len(loaded.reminders) == 1
    assert loaded.reminders[0].id == "r1"
    assert len(loaded.journal) == 1
    assert loaded.journal[0].id == "j1"

# Existing habit tests

def test_add_habit_creates_new_entry(tmp_path: Path):
    store = _default_store(tmp_path)
    habit = Habit(
        id="h2",
        anchor="After lunch",
        behavior="Read a page",
        celebration="Good job",
        emoji="📖",
        time_of_day="afternoon",
    )
    store.add_habit(habit)
    cfg = store.load()
    assert len(cfg.habits) == 1
    assert cfg.habits[0] == habit

def test_add_habit_raises_on_duplicate_id(tmp_path: Path):
    store = _default_store(tmp_path)
    habit = Habit(
        id="dup",
        anchor="x",
        behavior="y",
        celebration="z",
        emoji="🔔",
        time_of_day="any",
    )
    store.add_habit(habit)
    with pytest.raises(ValueError, match="already exists"):
        store.add_habit(habit)

def test_remove_habit_by_id(tmp_path: Path):
    store = _default_store(tmp_path)
    habit_a = Habit(
        id="a",
        anchor="a",
        behavior="a",
        celebration="a",
        emoji="🔹",
        time_of_day="any",
    )
    habit_b = Habit(
        id="b",
        anchor="b",
        behavior="b",
        celebration="b",
        emoji="🔸",
        time_of_day="any",
    )
    store.add_habit(habit_a)
    store.add_habit(habit_b)
    store.remove_habit("a")
    cfg = store.load()
    assert len(cfg.habits) == 1
    assert cfg.habits[0].id == "b"

# New tests for v0.2.0 features

def test_add_and_remove_reminder(tmp_path: Path):
    store = _default_store(tmp_path)
    reminder = Reminder(
        id="rem1",
        schedule="09:00",
        cadence="daily",
        message="Test reminder",
        habits=[],
    )
    store.add_reminder(reminder)
    cfg = store.load()
    assert len(cfg.reminders) == 1
    assert cfg.reminders[0] == reminder
    # remove
    store.remove_reminder("rem1")
    cfg = store.load()
    assert cfg.reminders == []

def test_add_and_remove_journal_prompt(tmp_path: Path):
    store = _default_store(tmp_path)
    prompt = JournalPrompt(id="jp1", label="Label", prompt="Ask?",
                          schedule="10:00", cadence="daily")
    store.add_journal_prompt(prompt)
    cfg = store.load()
    assert len(cfg.journal) == 1
    assert cfg.journal[0] == prompt
    store.remove_journal_prompt("jp1")
    cfg = store.load()
    assert cfg.journal == []

def test_add_and_remove_celebration(tmp_path: Path):
    store = _default_store(tmp_path)
    store.add_celebration("Yay!")
    cfg = store.load()
    assert cfg.celebrations == ["Yay!"]
    store.remove_celebration("Yay!")
    cfg = store.load()
    assert cfg.celebrations == []

def test_validation_catches_invalid_schedule(tmp_path: Path):
    store = _default_store(tmp_path)
    # invalid reminder schedule
    bad_reminder = Reminder(
        id="bad",
        schedule="invalid",
        cadence="daily",
        message="Oops",
        habits=[],
    )
    # add_reminder validates and should raise
    with pytest.raises(ValidationError):
        store.add_reminder(bad_reminder)

def test_load_nonexistent_returns_all_defaults(tmp_path: Path):
    store = _default_store(tmp_path)
    cfg = store.load()
    # ensure all new sections exist and are empty/default
    assert cfg.environment is not None
    assert cfg.celebrations == []
    assert cfg.reminders == []
    assert cfg.journal == []
