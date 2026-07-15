"""Coach engine for habit tracking.

Provides user‑facing messages for daily check‑ins, celebration, habit mention detection,
and logging prompts.
"""

from __future__ import annotations

from typing import List, Optional

from .models import Habit, CoachingConfig, Reminder


class Coach:
    """Generate messages based on a :class:`CoachingConfig` and a list of :class:`Habit`.

    The implementation follows a strict TDD approach – the public methods are exercised
    by the test suite in ``tests/test_coach.py``.
    """

    def __init__(self, config: CoachingConfig, celebrations: list[str] | None = None):
        """Instantiate a ``Coach``.

        The original implementation accepted only a ``CoachingConfig``. For v0.2.0 we
        add an optional ``celebrations`` list that is used by :pymeth:`next_celebration`.
        Existing callers that construct ``Coach`` without the second argument continue to
        work – a single generic celebration ("🎉") is supplied as a default.
        """
        self.config = config
        # Preserve backward compatibility: if the caller does not supply celebrations, use a
        # placeholder list containing a single emoji.
        self.celebrations = celebrations if celebrations is not None else ["🎉"]
        self._celebration_index = 0

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

    # ---------------------------------------------------------------------
    # New v0.2.0 API
    # ---------------------------------------------------------------------
    def next_celebration(self) -> str:
        """Return the next celebration string, rotating through ``self.celebrations``.

        The internal index is updated modulo the length of the celebrations list.
        """
        if not self.celebrations:
            return ""
        c = self.celebrations[self._celebration_index]
        self._celebration_index = (self._celebration_index + 1) % len(self.celebrations)
        return c

    def render_habit_list(self, habits: list[Habit], reminder: Reminder) -> str:
        """Render a habit list for a reminder.

        Only habits that are **active**, referenced by ``reminder.habits`` and not
        ``graduated_to_automatic`` are rendered. The rendering follows the spec provided
        in the task description.
        """
        # Filter relevant habits
        active_habits = [
            h
            for h in habits
            if h.id in reminder.habits
            and getattr(h, "active", False)
            and not getattr(h, "graduated_to_automatic", False)
        ]
        lines: list[str] = []
        for h in active_habits:
            if getattr(h, "faded", False):
                lines.append(
                    f"{h.emoji} ~~{h.behavior}~~ — {h.anchor} (having trouble? Let's talk about it)"
                )
            elif getattr(h, "chain_steps", None):
                first = h.chain_steps[0] if isinstance(h.chain_steps, list) and h.chain_steps else h.chain_steps
                lines.append(f"{h.emoji} {h.behavior} — Start: {first}")
            else:
                lines.append(f"{h.emoji} {h.behavior} — {h.anchor}")
        return "\n".join(lines)

    def graduated_coaching(self, habit: Habit) -> str:
        """Message for a habit that has become automatic (graduated)."""
        return (
            f"**{habit.behavior}** is automatic now — that's the goal working. "
            "Celebration is optional. Want to grow it or use this capacity for something new? "
            "Is the anchor still working for you?"
        )

    def faded_coaching(self, habit: Habit) -> str:
        """Message for a habit that is currently faded (skipped)."""
        return (
            f"You've been skipping **{habit.behavior}**. That's data, not failure. "
            "Let's look at B=MAP. Is it a Motivation issue? An Ability issue? A Prompt issue? "
            "If it feels hard, let's shrink it. What's the smallest version you could do? "
            "If the anchor isn't working, let's find a better one."
        )

    def build_reminder_message(self, reminder: Reminder, habits: list[Habit]) -> str:
        """Replace ``{habit_list}`` placeholder in ``reminder.message`` with rendered list.

        If the placeholder does not exist, the original message is returned unchanged.
        """
        habit_list = self.render_habit_list(habits, reminder)
        return reminder.message.replace("{habit_list}", habit_list)