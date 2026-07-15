import re
from datetime import datetime

class Scheduler:
    @staticmethod
    def reply_time_to_cron(time_str: str) -> str:
        """Convert HH:MM to cron minute hour * * *"""
        # Validate format
        if not re.fullmatch(r"\d{2}:\d{2}", time_str):
            raise ValueError("time_str must be HH:MM format")
        hour, minute = time_str.split(":")
        # Remove leading zeros for hour but keep minute as int (cron accepts 0-59)
        hour_int = int(hour)
        minute_int = int(minute)
        return f"{minute_int} {hour_int} * * *"

    @staticmethod
    def now_as_hhmm() -> str:
        """Return current time as HH:MM"""
        now = datetime.now()
        return now.strftime("%H:%M")

    @staticmethod
    def schedule_update_message(old_time: str, new_time: str) -> str:
        """Generate update message based on time change."""
        if old_time == new_time:
            return f"I'll check in with you at the same time tomorrow ({new_time})."
        else:
            return f"I've adjusted tomorrow's check-in to {new_time} to match when you're free."
