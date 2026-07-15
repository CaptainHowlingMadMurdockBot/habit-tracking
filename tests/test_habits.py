"""Tests for HabitStore YAML persistence using strict TDD.

The tests cover loading defaults, saving/loading round-trip, adding/removing habits,
and handling of duplicate IDs and missing files.
"""

import tempfile
from pathlib import Path

import pytest

from src.habitlib.models import Habit, CoachingConfig, HabitStoreConfig
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
    )
    store.save(cfg)
    loaded = store.load()
    assert loaded.coaching.style == "warm"
    assert loaded.coaching.missed_day_policy == "retry_once"
    assert loaded.coaching.schedule_time == "07:30"
    assert len(loaded.habits) == 1
    assert loaded.habits[0] == habit1


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
    # add both
    store.add_habit(habit_a)
    store.add_habit(habit_b)
    # remove one
    store.remove_habit("a")
    cfg = store.load()
    assert len(cfg.habits) == 1
    assert cfg.habits[0].id == "b"
