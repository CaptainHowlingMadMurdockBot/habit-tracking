import pytest
from src.habitlib.models import Habit, CoachingConfig
from src.habitlib.coach import Coach

def make_habit(id="h1", anchor="morning", behavior="drink water", celebration="yay", emoji="💧", time_of_day="07:00", active=True):
    return Habit(id=id, anchor=anchor, behavior=behavior, celebration=celebration, emoji=emoji, time_of_day=time_of_day, active=active)


def test_direct_style_checkin_one_habit():
    config = CoachingConfig(style="direct")
    coach = Coach(config)
    habit = make_habit()
    msg = coach.checkin([habit])
    assert "💧 drink water (morning)" in msg
    assert "Active habits: 1" in msg
    assert "How did it go? Reply with what you did!" in msg


def test_warm_style_checkin():
    config = CoachingConfig(style="warm")
    coach = Coach(config)
    habit = make_habit()
    msg = coach.checkin([habit])
    assert "How are you feeling about it?" in msg


def test_minimal_style_checkin():
    config = CoachingConfig(style="minimal")
    coach = Coach(config)
    habit = make_habit()
    msg = coach.checkin([habit])
    assert "Reply with your update." in msg


def test_checkin_no_active_habits():
    config = CoachingConfig(style="direct")
    coach = Coach(config)
    msg = coach.checkin([])
    assert "No active habits" in msg


def test_celebrate_direct():
    config = CoachingConfig(style="direct")
    coach = Coach(config)
    out = coach.celebrate("drink water")
    assert out == "✅ **drink water** — logged. Nice work."


def test_celebrate_warm():
    config = CoachingConfig(style="warm")
    coach = Coach(config)
    out = coach.celebrate("drink water")
    assert out == "🌟 **drink water** — that's awesome! You're building something real."


def test_celebrate_minimal():
    config = CoachingConfig(style="minimal")
    coach = Coach(config)
    out = coach.celebrate("drink water")
    assert out == "✅ drink water"


def test_detect_habit_mention_match():
    config = CoachingConfig(style="direct")
    coach = Coach(config)
    habit = make_habit(behavior="drink water", anchor="morning")
    msg = "I just drank water this morning"
    matched = coach.detect_habit_mention(msg, [habit])
    assert matched == habit


def test_detect_habit_mention_no_match():
    config = CoachingConfig(style="direct")
    coach = Coach(config)
    habit = make_habit(behavior="drink water", anchor="morning")
    msg = "I went for a run"
    matched = coach.detect_habit_mention(msg, [habit])
    assert matched is None


def test_logging_prompt():
    config = CoachingConfig(style="direct")
    coach = Coach(config)
    out = coach.logging_prompt("drink water", "💧")
    assert out == "Did you just do **drink water**? 💧 Want me to log it?"

