"""Coach engine for habit tracking.

Provides user‑facing messages for daily check‑ins, celebration, habit mention detection,
and logging prompts.
"""

from __future__ import annotations

from typing import List, Optional

from .models import Habit, CoachingConfig


class Coach:
    """Generate messages based on a :class:`CoachingConfig` and a list of :class:`Habit`.

    The implementation follows a strict TDD approach – the public methods are exercised
    by the test suite in ``tests/test_coach.py``.
    """

    def __init__(self, config: CoachingConfig):
        self.config = config

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------
    def _style_prompt(self) -> str:
        """Return the tail prompt string based on the configured style.

        The exact wording is required by the unit‑tests; only the *prefix*
        needs to be present for the assertions, but we emit the full sentence for
        completeness.
        """
        style = self.config.style
        if style == "direct":
            return (
                "How did it go? Reply with what you did! "
                "No worries if you missed one — tomorrow's a fresh start."
            )
        if style == "warm":
            return (
                "How are you feeling about it? I'm proud of you for showing up. "
                "And if today wasn't your day — that's okay. You're building something that lasts."
            )
        # minimal or any unknown fallback
        return "Reply with your update."

    # ---------------------------------------------------------------------
    # Public API required by the tests
    # ---------------------------------------------------------------------
    def checkin(self, habits: List[Habit]) -> str:
        """Generate a daily check‑in message.

        Parameters
        ----------
        habits:
            A list of :class:`Habit` objects. Only those with ``active`` set to
            ``True`` are listed.
        """
        active = [h for h in habits if getattr(h, "active", True)]
        if not active:
            return "No active habits to check‑in with."

        lines = [f"{h.emoji} {h.behavior} ({h.anchor})" for h in active]
        header = "\n".join(lines)
        count_line = f"Active habits: {len(active)}"
        prompt = self._style_prompt()
        return f"{header}\n{count_line}\n{prompt}"

    def celebrate(self, behavior: str) -> str:
        """Return a celebration message for *behavior* respecting the style.
        """
        style = self.config.style
        if style == "direct":
            return f"✅ **{behavior}** — logged. Nice work."
        if style == "warm":
            return f"🌟 **{behavior}** — that's awesome! You're building something real."
        # minimal or fallback
        return f"✅ {behavior}"

    def detect_habit_mention(self, message: str, habits: List[Habit]) -> Optional[Habit]:
        """Detect whether *message* mentions any habit.

        The detection scans ``behavior`` and ``anchor`` strings for words longer
        than three characters that appear (case‑insensitive) in ``message``.
        The first matching habit is returned; otherwise ``None``.
        """
        lowered = message.lower()
        for habit in habits:
            # combine behavior and anchor tokens
            tokens = habit.behavior.split() + habit.anchor.split()
            for token in tokens:
                if len(token) <= 3:
                    continue
                if token.lower() in lowered:
                    return habit
        return None

    def logging_prompt(self, behavior: str, emoji: str) -> str:
        """Return a confirmation prompt asking whether the user performed *behavior*.
        """
        return f"Did you just do **{behavior}**? {emoji} Want me to log it?"

