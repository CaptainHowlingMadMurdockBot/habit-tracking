"""HabitStore implementation with YAML persistence.

Provides methods to load, save, add, and remove habits using a YAML file.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from .models import Habit, CoachingConfig, HabitStoreConfig


class HabitStore:
    """Store and manage habits persisted as YAML.

    The file at ``path`` stores a mapping with optional ``coaching`` and ``habits`` keys.
    ``coaching`` maps to the fields of :class:`CoachingConfig`.
    ``habits`` is a list of habit dictionaries matching the :class:`Habit` dataclass.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    def _default_config(self) -> HabitStoreConfig:
        """Return a default configuration.

        Used when the file does not exist or is empty/invalid.
        """
        return HabitStoreConfig(coaching=CoachingConfig(), habits=[])

    def load(self) -> HabitStoreConfig:
        """Load the YAML configuration.

        Returns a :class:`HabitStoreConfig`. If the file does not exist or is empty,
        a default config is returned.
        """
        if not self.path.exists():
            return self._default_config()
        try:
            raw = self.path.read_text()
        except Exception:
            return self._default_config()
        if not raw.strip():
            return self._default_config()
        try:
            data = yaml.safe_load(raw) or {}
        except yaml.YAMLError:
            # Corrupt YAML – fall back to defaults
            return self._default_config()
        # Parse coaching
        coaching_data = data.get("coaching", {})
        coaching = CoachingConfig(**coaching_data) if isinstance(coaching_data, dict) else CoachingConfig()
        # Parse habits list
        habits_raw = data.get("habits", [])
        habits: list[Habit] = []
        if isinstance(habits_raw, list):
            for h in habits_raw:
                if isinstance(h, dict):
                    try:
                        habit = Habit(**h)
                    except TypeError:
                        # Missing required fields – skip
                        continue
                    habits.append(habit)
        return HabitStoreConfig(coaching=coaching, habits=habits)

    def save(self, config: HabitStoreConfig) -> None:
        """Save ``config`` to the YAML file.

        The file's parent directory is created if missing.
        """
        data: dict[str, Any] = {
            "coaching": {
                "style": config.coaching.style,
                "missed_day_policy": config.coaching.missed_day_policy,
                "schedule_time": config.coaching.schedule_time,
            },
            "habits": [
                {
                    "id": h.id,
                    "anchor": h.anchor,
                    "behavior": h.behavior,
                    "celebration": h.celebration,
                    "emoji": h.emoji,
                    "time_of_day": h.time_of_day,
                    "active": h.active,
                }
                for h in config.habits
            ],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(yaml.safe_dump(data, sort_keys=False))

    def add_habit(self, habit: Habit) -> None:
        """Add a new habit.

        Raises ``ValueError`` if a habit with the same ``id`` already exists.
        """
        cfg = self.load()
        if any(h.id == habit.id for h in cfg.habits):
            raise ValueError(f"Habit with id '{habit.id}' already exists")
        cfg.habits.append(habit)
        self.save(cfg)

    def remove_habit(self, habit_id: str) -> None:
        """Remove a habit by its identifier.

        If the habit does not exist, the method does nothing.
        """
        cfg = self.load()
        cfg.habits = [h for h in cfg.habits if h.id != habit_id]
        self.save(cfg)
