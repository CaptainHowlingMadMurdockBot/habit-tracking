"""Data models for the habit-tracking library.

Defines dataclasses for Habit, CoachingConfig, and HabitStoreConfig.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Habit:
    id: str
    anchor: str
    behavior: str
    celebration: str
    emoji: str
    time_of_day: str
    active: bool = True
    chain_steps: List[str] = field(default_factory=list)
    graduated_to_automatic: bool = False
    faded: bool = False
    emoji_variants: List[str] = field(default_factory=list)

@dataclass
class CoachingConfig:
    style: str = "direct"  # "direct", "warm", "minimal"
    missed_day_policy: str = "fire_and_forget"  # "fire_and_forget", "retry_once", "pause_after_3"
    schedule_time: str = "20:00"  # HH:MM 24h format


@dataclass
class DailyLogConfig:
    enabled: bool = True
    path: str = ""

@dataclass
class TimeBoundaries:
    morning_cutoff: str = "15:00"
    cat_dinner_cutoff: str = "17:00"

@dataclass
class EnvironmentConfig:
    daily_log: DailyLogConfig = field(default_factory=DailyLogConfig)
    time_boundaries: TimeBoundaries = field(default_factory=TimeBoundaries)

@dataclass
class Reminder:
    id: str
    schedule: str
    cadence: str
    message: str
    habits: List[str]
    follow_up_delay: int | None = None

@dataclass
class JournalPrompt:
    id: str
    label: str
    prompt: str
    schedule: str | None = None
    cadence: str | None = None
    conversational: bool = True

@dataclass
class HabitStoreConfig:
    coaching: CoachingConfig = field(default_factory=CoachingConfig)
    habits: List[Habit] = field(default_factory=list)
    # New sections for v0.2.0
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    celebrations: List[str] = field(default_factory=list)
    reminders: List[Reminder] = field(default_factory=list)
    journal: List[JournalPrompt] = field(default_factory=list)

class ValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

def _is_valid_time(s: str) -> bool:
    import re
    return bool(re.fullmatch(r"\d{2}:\d{2}", s))

def validate_config(config: HabitStoreConfig) -> None:
    # Check habit contradictions
    for habit in config.habits:
        if getattr(habit, "graduated_to_automatic", False) and getattr(habit, "faded", False):
            raise ValidationError(
                f"Habit {habit.id} cannot have both graduated_to_automatic and faded set to True."
            )
    # Prepare set of habit ids
    habit_ids = {habit.id for habit in config.habits}
    # Validate reminders
    for reminder in getattr(config, "reminders", []):
        if not _is_valid_time(reminder.schedule):
            raise ValidationError(
                f"Reminder {reminder.id} has invalid schedule '{reminder.schedule}'. Expected HH:MM format."
            )
        for h_id in reminder.habits:
            if h_id not in habit_ids:
                raise ValidationError(
                                        f"Reminder {reminder.id} has habit reference error: unknown habit id '{h_id}'."
                                    )

