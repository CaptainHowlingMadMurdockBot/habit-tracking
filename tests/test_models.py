import sys, os
sys.path.append(os.path.abspath('src'))

from src.habitlib.models import Habit, CoachingConfig, HabitStoreConfig



def test_habit_default_active():
    habit = Habit(id="h2", anchor="x", behavior="y", celebration="z", emoji="🔔", time_of_day="any")
    assert habit.active is True

def test_coachingconfig_defaults():
    cfg = CoachingConfig()
    assert cfg.style == "direct"
    assert cfg.missed_day_policy == "fire_and_forget"
    assert cfg.schedule_time == "20:00"

def test_coachingconfig_custom():
    cfg = CoachingConfig(style="warm", missed_day_policy="retry_once", schedule_time="07:30")
    assert cfg.style == "warm"
    assert cfg.missed_day_policy == "retry_once"
    assert cfg.schedule_time == "07:30"

def test_habitstoreconfig_with_habits():
    habit = Habit(id="h3", anchor="a", behavior="b", celebration="c", emoji="👍", time_of_day="evening")
    store = HabitStoreConfig(habits=[habit])
    assert isinstance(store.coaching, CoachingConfig)
    assert len(store.habits) == 1
    assert store.habits[0] == habit

def test_habitstoreconfig_empty_defaults():
    store = HabitStoreConfig()
    assert isinstance(store.coaching, CoachingConfig)
    assert store.habits == []

    habit = Habit(
        id="habit1",
        anchor="After I pour my morning coffee",
        behavior="I will take my vitamins",
        celebration="I did it!",
        emoji="💊",
        time_of_day="morning",
        active=False,
    )
    assert habit.id == "habit1"
    assert habit.anchor == "After I pour my morning coffee"
    assert habit.behavior == "I will take my vitamins"
    assert habit.celebration == "I did it!"
    assert habit.emoji == "💊"
    assert habit.time_of_day == "morning"
    assert habit.active is False
