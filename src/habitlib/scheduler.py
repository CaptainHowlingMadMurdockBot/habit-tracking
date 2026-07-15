import re
from datetime import datetime
from .models import Reminder

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

    # ---------------------------------------------------------------------
    # New v0.2.0 functionality
    # ---------------------------------------------------------------------
    @staticmethod
    def _weekday_index() -> int:
        """Return the current weekday as an integer where Monday is 0.

        Separated into its own method to make it easy to patch in tests.
        """
        return datetime.now().weekday()

    @staticmethod
    def matches_cadence(cadence: str) -> bool:
        """Return ``True`` if *today* matches the provided ``cadence`` string.

        Supported cadence formats:
        - ``daily`` – always matches
        - ``weekdays`` – Monday through Friday
        - ``weekends`` – Saturday and Sunday
        - full day name (e.g. ``monday``)
        - underscore‑separated list of abbreviated days (e.g. ``mon_wed_fri``)

        The function is case‑insensitive.
        """
        today = Scheduler._weekday_index()
        cadence = cadence.lower()

        # Simple cases
        if cadence == "daily":
            return True
        if cadence == "weekdays":
            return 0 <= today <= 4
        if cadence == "weekends":
            return today >= 5

        # Mapping of day names / abbreviations to weekday index
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
            "mon": 0,
            "tue": 1,
            "wed": 2,
            "thu": 3,
            "fri": 4,
            "sat": 5,
            "sun": 6,
        }

        # Direct day name
        if cadence in day_map:
            return today == day_map[cadence]

        # Underscore list (e.g. mon_wed_fri)
        parts = cadence.split("_")
        for part in parts:
            if part in day_map and today == day_map[part]:
                return True
        return False

    @staticmethod
    def _parse_time_to_minutes(time_str: str) -> int:
        """Convert ``HH:MM`` to minutes since midnight.

        Raises ``ValueError`` if the format is invalid.
        """
        if not re.fullmatch(r"\d{2}:\d{2}", time_str):
            raise ValueError("time_str must be HH:MM format")
        hour, minute = map(int, time_str.split(":"))
        return hour * 60 + minute

    @staticmethod
    def due_reminders(reminders: list[Reminder], current_time: str | None = None) -> list[Reminder]:
        """Return reminders that are due right now.

        A reminder is *due* when its ``schedule`` matches ``current_time`` (or the
        current clock if ``current_time`` is ``None``) **and** its cadence matches
        today.
        """
        if current_time is None:
            current_time = Scheduler.now_as_hhmm()
        due = []
        for r in reminders:
            if r.schedule == current_time and Scheduler.matches_cadence(r.cadence):
                due.append(r)
        return due

    @staticmethod
    def follow_up_due(reminder: Reminder, current_time: str) -> bool:
        """Determine whether a follow‑up nudge is due.

        The follow‑up is due when ``current_time`` equals the reminder's scheduled
        time plus ``follow_up_delay`` minutes. If ``follow_up_delay`` is ``None`` the
        function returns ``False``.
        """
        if reminder.follow_up_delay is None:
            return False
        try:
            schedule_min = Scheduler._parse_time_to_minutes(reminder.schedule)
            current_min = Scheduler._parse_time_to_minutes(current_time)
        except ValueError:
            return False
        target = schedule_min + reminder.follow_up_delay
        return current_min == target
