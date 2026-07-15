# Habit Tracking — Tiny Habits for Hermes Agent

A reusable, open-source habit tracking system for [Hermes Agent](https://hermes-agent.nousresearch.com), built on BJ Fogg's Tiny Habits methodology.

## What it does

- **Conversational setup** — guided onboarding that teaches Tiny Habits principles
- **Single master cron job** — one daily check-in, dynamically scheduled to match your rhythm
- **Non-judgemental coaching** — three styles (direct, warm, minimal), configurable per user
- **Conversational logging** — mention doing a habit in chat and the bot offers to log it
- **Dynamic scheduling** — the check-in time shifts to when you actually engage

## Quick start

1. Install the skill on your Hermes profile
2. Say "I want to set up habits"
3. Follow the guided setup (1-2 habits to start)
4. The master cron job handles the rest

## Architecture

```
skill/SKILL.md          — Hermes skill loaded by the agent
skill/habits.yaml       — Persistent habit data (managed by the agent)
skill/scripts/setup.py  — Setup script for initial configuration
src/habitlib/           — Python library (models, coach, scheduler, persistence)
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
