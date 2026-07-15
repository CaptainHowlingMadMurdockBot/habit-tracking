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


@dataclass
class CoachingConfig:
    style: str = "direct"  # "direct", "warm", "minimal"
    missed_day_policy: str = "fire_and_forget"  # "fire_and_forget", "retry_once", "pause_after_3"
    schedule_time: str = "20:00"  # HH:MM 24h format


@dataclass
class HabitStoreConfig:
    coaching: CoachingConfig = field(default_factory=CoachingConfig)
    habits: List[Habit] = field(default_factory=list)
