import pytest
from src.habitlib.models import Habit, CoachingConfig, Reminder
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

# ---------------------------------------------------------------------
# New v0.2.0 tests
# ---------------------------------------------------------------------

def make_reminder(message="Reminder: {habit_list}", habits=None):
    if habits is None:
        habits = []
    # Reminder fields: id, schedule, cadence, message, habits, follow_up_delay
    return Reminder(id="r1", schedule="2023-01-01", cadence="daily", message=message, habits=habits, follow_up_delay=0)

def test_celebration_rotation_cycles():
    config = CoachingConfig(style="direct")
    coach = Coach(config, celebrations=["🎉", "👏", "🥳"])
    assert coach.next_celebration() == "🎉"
    assert coach.next_celebration() == "👏"
    assert coach.next_celebration() == "🥳"

def test_celebration_rotation_wraps():
    config = CoachingConfig(style="direct")
    coach = Coach(config, celebrations=["🙌"])
    assert coach.next_celebration() == "🙌"
    assert coach.next_celebration() == "🙌"

def test_render_habit_list_excludes_graduated():
    habit1 = Habit(id="h1", anchor="morning", behavior="drink water", celebration="yay", emoji="💧", time_of_day="07:00", active=True, graduated_to_automatic=True)
    habit2 = Habit(id="h2", anchor="evening", behavior="read book", celebration="yay", emoji="📚", time_of_day="20:00", active=True)
    reminder = make_reminder(habits=["h1", "h2"])
    coach = Coach(CoachingConfig(style="direct"))
    rendered = coach.render_habit_list([habit1, habit2], reminder)
    # Only habit2 should appear
    assert "📚 read book — evening" in rendered
    assert "💧" not in rendered

def test_render_habit_list_faded_message():
    habit = Habit(id="h1", anchor="morning", behavior="drink water", celebration="yay", emoji="💧", time_of_day="07:00", active=True, faded=True)
    reminder = make_reminder(habits=["h1"])
    coach = Coach(CoachingConfig(style="direct"))
    rendered = coach.render_habit_list([habit], reminder)
    expected = "💧 ~~drink water~~ — morning (having trouble? Let's talk about it)"
    assert rendered == expected

def test_render_habit_list_chain_steps():
    habit = Habit(id="h1", anchor="morning", behavior="run", celebration="yay", emoji="🏃", time_of_day="07:00", active=True, chain_steps=["stretch", "jog"])
    reminder = make_reminder(habits=["h1"])
    coach = Coach(CoachingConfig(style="direct"))
    rendered = coach.render_habit_list([habit], reminder)
    assert rendered == "🏃 run — Start: stretch"

def test_render_habit_list_normal():
    habit = Habit(id="h1", anchor="morning", behavior="drink water", celebration="yay", emoji="💧", time_of_day="07:00", active=True)
    reminder = make_reminder(habits=["h1"])
    coach = Coach(CoachingConfig(style="direct"))
    rendered = coach.render_habit_list([habit], reminder)
    assert rendered == "💧 drink water — morning"

def test_graduated_coaching_message():
    habit = Habit(id="h1", anchor="morning", behavior="drink water", celebration="yay", emoji="💧", time_of_day="07:00", active=True, graduated_to_automatic=True)
    coach = Coach(CoachingConfig(style="direct"))
    msg = coach.graduated_coaching(habit)
    assert "**drink water** is automatic now" in msg

def test_faded_coaching_message():
    habit = Habit(id="h1", anchor="morning", behavior="drink water", celebration="yay", emoji="💧", time_of_day="07:00", active=True, faded=True)
    coach = Coach(CoachingConfig(style="direct"))
    msg = coach.faded_coaching(habit)
    assert "You've been skipping **drink water**" in msg

def test_build_reminder_message_substitutes():
    habit = Habit(id="h1", anchor="morning", behavior="drink water", celebration="yay", emoji="💧", time_of_day="07:00", active=True)
    reminder = make_reminder(message="Start your day: {habit_list}", habits=["h1"])
    coach = Coach(CoachingConfig(style="direct"))
    result = coach.build_reminder_message(reminder, [habit])
    assert "💧 drink water — morning" in result
    assert "{habit_list}" not in result

def test_build_reminder_message_empty_list():
    reminder = make_reminder(message="No habits: {habit_list}", habits=[])
    coach = Coach(CoachingConfig(style="direct"))
    result = coach.build_reminder_message(reminder, [])
    assert result == "No habits: "

