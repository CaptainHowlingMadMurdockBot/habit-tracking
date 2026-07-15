"""HabitStore implementation with YAML persistence.

Provides methods to load, save, add, and remove habits using a YAML file.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from .models import (
    Habit,
    CoachingConfig,
    HabitStoreConfig,
    EnvironmentConfig,
    Reminder,
    JournalPrompt,
    ValidationError,
    validate_config,
)


class HabitStore:
    """Store and manage habits persisted as YAML.

    The file at ``path`` stores a mapping with optional ``coaching`` and ``habits`` keys.
    ``coaching`` maps to the fields of :class:`CoachingConfig`.
    ``habits`` is a list of habit dictionaries matching the :class:`Habit` dataclass.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    def _default_config(self) -> HabitStoreConfig:
        """Return a default configuration for the expanded schema.

        Includes all sections with their defaults.
        """
        # EnvironmentConfig, Reminder, JournalPrompt are imported at top
        return HabitStoreConfig(
            coaching=CoachingConfig(),
            habits=[],
            environment=EnvironmentConfig(),
            celebrations=[],
            reminders=[],
            journal=[],
        )

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
        # Parse environment
        env_data = data.get("environment", {})
        daily_log_data = env_data.get("daily_log", {})
        time_boundaries_data = env_data.get("time_boundaries", {})
        from .models import EnvironmentConfig, DailyLogConfig, TimeBoundaries
        daily_log = DailyLogConfig(**daily_log_data) if isinstance(daily_log_data, dict) else DailyLogConfig()
        time_boundaries = TimeBoundaries(**time_boundaries_data) if isinstance(time_boundaries_data, dict) else TimeBoundaries()
        environment = EnvironmentConfig(daily_log=daily_log, time_boundaries=time_boundaries)
        # Parse celebrations
        celebrations = data.get("celebrations", []) if isinstance(data.get("celebrations", []), list) else []
        # Parse reminders
        reminders_raw = data.get("reminders", [])
        reminders: list[Reminder] = []
        if isinstance(reminders_raw, list):
            for r in reminders_raw:
                if isinstance(r, dict):
                    try:
                        reminder = Reminder(**r)
                    except TypeError:
                        continue
                    reminders.append(reminder)
        # Parse journal prompts
        journal_raw = data.get("journal", [])
        journal: list[JournalPrompt] = []
        if isinstance(journal_raw, list):
            for p in journal_raw:
                if isinstance(p, dict):
                    try:
                        prompt = JournalPrompt(**p)
                    except TypeError:
                        continue
                    journal.append(prompt)
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
        return HabitStoreConfig(
            coaching=coaching,
            habits=habits,
            environment=environment,
            celebrations=celebrations,
            reminders=reminders,
            journal=journal,
        )

    def save(self, config: HabitStoreConfig) -> None:
        """Save ``config`` to the YAML file.

        The file's parent directory is created if missing.
        """
        # Validate before saving
        self.validate(config)
        data: dict[str, Any] = {
            "coaching": {
                "style": config.coaching.style,
                "missed_day_policy": config.coaching.missed_day_policy,
                "schedule_time": config.coaching.schedule_time,
            },
            "environment": {
                "daily_log": {
                    "enabled": config.environment.daily_log.enabled,
                    "path": config.environment.daily_log.path,
                },
                "time_boundaries": {
                    "morning_cutoff": config.environment.time_boundaries.morning_cutoff,
                    "cat_dinner_cutoff": config.environment.time_boundaries.cat_dinner_cutoff,
                },
            },
            "celebrations": config.celebrations,
            "reminders": [
                {
                    "id": r.id,
                    "schedule": r.schedule,
                    "cadence": r.cadence,
                    "message": r.message,
                    "habits": r.habits,
                    "follow_up_delay": r.follow_up_delay,
                }
                for r in config.reminders
            ],
            "journal": [
                {
                    "id": p.id,
                    "label": p.label,
                    "prompt": p.prompt,
                    "schedule": p.schedule,
                    "cadence": p.cadence,
                    "conversational": p.conversational,
                }
                for p in config.journal
            ],
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
        cfg = self.load()
        if any(h.id == habit.id for h in cfg.habits):
            raise ValueError(f"Habit with id '{habit.id}' already exists")
        cfg.habits.append(habit)
        # Validate config before saving
        self.validate(cfg)
        self.save(cfg)

    def remove_habit(self, habit_id: str) -> None:
        cfg = self.load()
        cfg.habits = [h for h in cfg.habits if h.id != habit_id]
        # Validate config before saving
        self.validate(cfg)
        self.save(cfg)

    # Additional v0.2.0 methods
    def add_reminder(self, reminder: Reminder) -> None:
        cfg = self.load()
        if any(r.id == reminder.id for r in cfg.reminders):
            raise ValueError(f"Reminder with id '{reminder.id}' already exists")
        cfg.reminders.append(reminder)
        self.validate(cfg)
        self.save(cfg)

    def remove_reminder(self, reminder_id: str) -> None:
        cfg = self.load()
        cfg.reminders = [r for r in cfg.reminders if r.id != reminder_id]
        self.validate(cfg)
        self.save(cfg)

    def add_journal_prompt(self, prompt: JournalPrompt) -> None:
        cfg = self.load()
        if any(p.id == prompt.id for p in cfg.journal):
            raise ValueError(f"JournalPrompt with id '{prompt.id}' already exists")
        cfg.journal.append(prompt)
        self.validate(cfg)
        self.save(cfg)

    def remove_journal_prompt(self, prompt_id: str) -> None:
        cfg = self.load()
        cfg.journal = [p for p in cfg.journal if p.id != prompt_id]
        self.validate(cfg)
        self.save(cfg)

    def add_celebration(self, celebration: str) -> None:
        cfg = self.load()
        cfg.celebrations.append(celebration)
        self.validate(cfg)
        self.save(cfg)

    def remove_celebration(self, celebration: str) -> None:
        cfg = self.load()
        cfg.celebrations = [c for c in cfg.celebrations if c != celebration]
        self.validate(cfg)
        self.save(cfg)

    def validate(self, config: HabitStoreConfig | None = None) -> None:
        """Validate the configuration using ``validate_config``.

        If ``config`` is ``None``, loads the current config and validates it.
        """
        if config is None:
            config = self.load()
        validate_config(config)
