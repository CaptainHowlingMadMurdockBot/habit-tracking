import sys, os
sys.path.append(os.path.abspath('src'))

from src.habitlib.models import Habit, CoachingConfig, HabitStoreConfig, DailyLogConfig, TimeBoundaries, EnvironmentConfig, Reminder, JournalPrompt, ValidationError, validate_config



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



def test_dailylogconfig_defaults():
    cfg = DailyLogConfig()
    assert cfg.enabled is True
    assert cfg.path == ""

def test_timeboundaries_defaults():
    tb = TimeBoundaries()
    assert tb.morning_cutoff == "15:00"
    assert tb.cat_dinner_cutoff == "17:00"

def test_environmentconfig_nested():
    env = EnvironmentConfig()
    assert isinstance(env.daily_log, DailyLogConfig)
    assert isinstance(env.time_boundaries, TimeBoundaries)

def test_reminder_creation_all_fields():
    rem = Reminder(
        id="r1",
        schedule="06:00",
        cadence="daily",
        message="Do {habit_list}",
        habits=["h1"],
        follow_up_delay=10,
    )
    assert rem.id == "r1"
    assert rem.schedule == "06:00"
    assert rem.cadence == "daily"
    assert rem.message == "Do {habit_list}"
    assert rem.habits == ["h1"]
    assert rem.follow_up_delay == 10

def test_reminder_no_follow_up_delay():
    rem = Reminder(
        id="r2",
        schedule="07:30",
        cadence="weekdays",
        message="Reminder",
        habits=["h2"],
    )
    assert rem.follow_up_delay is None

def test_journalprompt_creation():
    jp = JournalPrompt(
        id="j1",
        label="Morning",
        prompt="How are you?",
        schedule="08:00",
        cadence="daily",
        conversational=False,
    )
    assert jp.id == "j1"
    assert jp.label == "Morning"
    assert jp.prompt == "How are you?"
    assert jp.schedule == "08:00"
    assert jp.cadence == "daily"
    assert jp.conversational is False

def test_journalprompt_conversational_only():
    jp = JournalPrompt(
        id="j2",
        label="Evening",
        prompt="Reflect",
    )
    assert jp.schedule is None
    assert jp.cadence is None
    assert jp.conversational is True

def test_habit_chain_steps():
    habit = Habit(id="h1", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any", chain_steps=["step1", "step2"])
    assert habit.chain_steps == ["step1", "step2"]

def test_habit_graduated_to_automatic():
    habit = Habit(id="h2", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any", graduated_to_automatic=True)
    assert habit.graduated_to_automatic is True

def test_habit_faded():
    habit = Habit(id="h3", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any", faded=True)
    assert habit.faded is True

def test_habit_emoji_variants():
    habit = Habit(id="h4", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any", emoji_variants=["😀","😃"])
    assert habit.emoji_variants == ["😀","😃"]

def test_habitstoreconfig_all_sections():
    env = EnvironmentConfig()
    reminder = Reminder(id="r1", schedule="06:00", cadence="daily", message="msg", habits=["h1"])
    jp = JournalPrompt(id="j1", label="L", prompt="P")
    store = HabitStoreConfig(
        environment=env,
        celebrations=["cheer"],
        reminders=[reminder],
        journal=[jp],
        habits=[],
    )
    assert isinstance(store.environment, EnvironmentConfig)
    assert store.celebrations == ["cheer"]
    assert store.reminders == [reminder]
    assert store.journal == [jp]

def test_validate_config_passes():
    habit = Habit(id="h1", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any")
    reminder = Reminder(id="r1", schedule="06:00", cadence="daily", message="msg", habits=["h1"])
    cfg = HabitStoreConfig(habits=[habit], reminders=[reminder])
    # should not raise
    validate_config(cfg)

def test_validate_config_graduated_and_faded_error():
    habit = Habit(id="h1", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any", graduated_to_automatic=True, faded=True)
    cfg = HabitStoreConfig(habits=[habit])
    try:
        validate_config(cfg)
    except ValidationError as e:
        assert "graduated_to_automatic and faded" in str(e)
    else:
        assert False, "ValidationError not raised"

def test_validate_config_invalid_schedule_error():
    habit = Habit(id="h1", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any")
    reminder = Reminder(id="r1", schedule="6am", cadence="daily", message="msg", habits=["h1"])
    cfg = HabitStoreConfig(habits=[habit], reminders=[reminder])
    try:
        validate_config(cfg)
    except ValidationError as e:
        assert "invalid schedule" in str(e).lower()
    else:
        assert False, "ValidationError not raised"

def test_validate_config_missing_habit_reference_error():
    habit = Habit(id="h1", anchor="a", behavior="b", celebration="c", emoji="😀", time_of_day="any")
    reminder = Reminder(id="r1", schedule="06:00", cadence="daily", message="msg", habits=["missing"])
    cfg = HabitStoreConfig(habits=[habit], reminders=[reminder])
    try:
        validate_config(cfg)
    except ValidationError as e:
        assert "habit reference" in str(e).lower()
    else:
        assert False, "ValidationError not raised"
