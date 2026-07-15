import re
import sys, os
sys.path.append(os.path.abspath('src'))

from src.habitlib.scheduler import Scheduler
from src.habitlib.models import Reminder

def test_matches_cadence_daily(monkeypatch):
    # weekday irrelevant, set to Wednesday (2)
    monkeypatch.setattr(Scheduler, "_weekday_index", lambda: 2)
    assert Scheduler.matches_cadence("daily") is True

def test_matches_cadence_mon_wed_fri_monday(monkeypatch):
    monkeypatch.setattr(Scheduler, "_weekday_index", lambda: 0)  # Monday
    assert Scheduler.matches_cadence("mon_wed_fri") is True

def test_matches_cadence_mon_wed_fri_tuesday(monkeypatch):
    monkeypatch.setattr(Scheduler, "_weekday_index", lambda: 1)  # Tuesday
    assert Scheduler.matches_cadence("mon_wed_fri") is False

def test_matches_cadence_sunday_true(monkeypatch):
    monkeypatch.setattr(Scheduler, "_weekday_index", lambda: 6)  # Sunday
    assert Scheduler.matches_cadence("sunday") is True

def test_matches_cadence_sunday_false(monkeypatch):
    monkeypatch.setattr(Scheduler, "_weekday_index", lambda: 0)  # Monday
    assert Scheduler.matches_cadence("sunday") is False

def test_matches_cadence_weekdays_wednesday(monkeypatch):
    monkeypatch.setattr(Scheduler, "_weekday_index", lambda: 2)  # Wednesday
    assert Scheduler.matches_cadence("weekdays") is True

def test_matches_cadence_weekdays_saturday(monkeypatch):
    monkeypatch.setattr(Scheduler, "_weekday_index", lambda: 5)  # Saturday
    assert Scheduler.matches_cadence("weekdays") is False

def test_due_reminders_matching():
    reminder = Reminder(id="r1", schedule="09:00", cadence="daily", message="msg", habits=[], follow_up_delay=None)
    due = Scheduler.due_reminders([reminder], current_time="09:00")
    assert due == [reminder]

def test_due_reminders_none():
    reminder = Reminder(id="r1", schedule="09:00", cadence="daily", message="msg", habits=[], follow_up_delay=None)
    due = Scheduler.due_reminders([reminder], current_time="10:00")
    assert due == []

def test_follow_up_due_true():
    reminder = Reminder(id="r1", schedule="09:00", cadence="daily", message="msg", habits=[], follow_up_delay=15)
    assert Scheduler.follow_up_due(reminder, "09:15") is True

def test_follow_up_due_no_delay_false():
    reminder = Reminder(id="r1", schedule="09:00", cadence="daily", message="msg", habits=[], follow_up_delay=None)
    assert Scheduler.follow_up_due(reminder, "09:15") is False

def test_follow_up_due_wrong_time_false():
    reminder = Reminder(id="r1", schedule="09:00", cadence="daily", message="msg", habits=[], follow_up_delay=15)
    assert Scheduler.follow_up_due(reminder, "09:20") is False

