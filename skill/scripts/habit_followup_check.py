#!/usr/bin/env python3
"""
Silent-check follow-up for habit coaching.

Runs after a coaching nudge to check if habits have been logged.
If habits are found in today's daily log: exits silently (no output = no message sent).
If not found: prints a gentle "could"-framed nudge.

Usage: Called by the master cron job's follow-up logic, or scheduled as a no_agent=True cron job.
The script reads habits.yaml to determine which habits to check and what nudge to send.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime

# Default skill directory (can be overridden via env var)
SKILL_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".hermes" / "skills" / "habit-tracking"
HABITS_PATH = SKILL_DIR / "habits.yaml"


def main():
    if not HABITS_PATH.exists():
        print("habits.yaml not found — cannot check follow-up status.")
        sys.exit(0)

    with open(HABITS_PATH) as f:
        data = yaml.safe_load(f) or {}

    # Get daily log path from environment config
    env = data.get("environment", {})
    daily_log = env.get("daily_log", {})
    log_path_template = daily_log.get("path", "")
    log_enabled = daily_log.get("enabled", False)

    if not log_enabled or not log_path_template:
        # No daily log configured — can't check, stay silent
        sys.exit(0)

    # Build today's log path
    today = datetime.now().strftime("%Y-%m-%d")
    log_path_str = log_path_template.replace("{date}", today)
    log_path = Path(log_path_str)

    # Collect all habit emojis from the config
    habits = data.get("habits", [])
    all_emojis = set()
    for h in habits:
        if h.get("active", True):
            all_emojis.add(h.get("emoji", ""))
            for variant in h.get("emoji_variants", []):
                all_emojis.add(variant)
    all_emojis.discard("")

    # Check today's log for any habit emojis
    if log_path.exists():
        content = log_path.read_text()
        if any(emoji in content for emoji in all_emojis):
            # Habits are being tracked — stay silent
            sys.exit(0)

    # No habits found — send a gentle nudge
    hour = datetime.now().hour
    period = "evening" if hour >= 17 else "morning"

    # Build nudge from active habits
    active_habits = [h for h in habits if h.get("active", True) and not h.get("graduated_to_automatic", False)]
    if not active_habits:
        sys.exit(0)

    emoji_list = " ".join(h.get("emoji", "✅") for h in active_habits)
    if period == "evening":
        print(f"Hey — no pressure at all, just a gentle nudge. "
              f"There are some things you could do tonight. "
              f"{emoji_list} "
              f"These are 'coulds,' not 'shoulds.'")
    else:
        print(f"Hey — no pressure at all, just a gentle nudge. "
              f"There are some things you could do this morning. "
              f"{emoji_list} "
              f"These are 'coulds,' not 'shoulds.'")


if __name__ == "__main__":
    main()
