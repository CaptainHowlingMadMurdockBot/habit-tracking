import re
import sys, os
sys.path.append(os.path.abspath('src'))

from src.habitlib.scheduler import Scheduler

def test_reply_time_to_cron_evening():
    assert Scheduler.reply_time_to_cron("23:47") == "47 23 * * *"

def test_reply_time_to_cron_midnight():
    assert Scheduler.reply_time_to_cron("00:15") == "15 0 * * *"

def test_reply_time_to_cron_morning():
    assert Scheduler.reply_time_to_cron("08:00") == "0 8 * * *"

def test_schedule_update_message_same():
    msg = Scheduler.schedule_update_message("09:30", "09:30")
    assert msg == "I'll check in with you at the same time tomorrow (09:30)."

def test_schedule_update_message_changed():
    msg = Scheduler.schedule_update_message("09:30", "10:45")
    assert msg == "I've adjusted tomorrow's check-in to 10:45 to match when you're free."

def test_now_as_hhmm_format():
    result = Scheduler.now_as_hhmm()
    assert re.fullmatch(r"\d{2}:\d{2}", result), f"Unexpected format: {result}"
