---
name: habit-tracking
description: "Tiny Habits-based habit tracking — multi-reminder scheduling, dynamic cadences, graduated/automatic and faded habit coaching, celebration rotation, journal prompts, daily logging. Inspired by BJ Fogg's research."
version: 0.2.0
author: Hermes Agent (inspired by BJ Fogg's Tiny Habits methodology)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [habits, coaching, tiny-habits, productivity, wellness, reminders]
    related_skills: [cronjob, reminder-management]
---

# Habit Tracking — Tiny Habits for Hermes Agent

## Attribution

This skill is inspired by **BJ Fogg's Tiny Habits** methodology and research. BJ Fogg has **not endorsed** this project. For the full methodology, visit:

- [bjfogg.com](https://www.bjfogg.com)
- [tinyhabits.com](https://tinyhabits.com)
- *Tiny Habits: The Small Changes That Change Everything* (Fogg, 2020, ISBN 978-1524750261)

---

## Overview

This skill provides a complete habit tracking system built on BJ Fogg's Tiny Habits methodology. It uses a **single master cron job running hourly** that checks which reminders are due based on schedule + cadence, sends those reminders, and checks for follow-up nudges.

**Core principles:**
- **Start small** — 1-2 habits at a time, tiny enough to feel easy
- **Anchor → Behavior → Celebration** — the Tiny Habits formula
- **Non-judgemental** — "could" not "should", missed days are data not failure
- **Adaptive** — the check-in time shifts to match when you actually engage
- **Conversational** — mention doing a habit and the bot offers to log it
- **Graduated habits** — automatic habits get growth coaching, not reminders
- **Faded habits** — skipped habits get B=MAP troubleshooting, not guilt

---

## YAML Schema Reference

The entire system is configured through `habits.yaml`. Here's the full schema:

### environment

Per-user, per-install configuration.

```yaml
environment:
  daily_log:
    enabled: true
    path: "/mnt/obsidian-vaults/eman-mobile/Daily/{date}.md"
    # {date} is replaced with YYYY-MM-DD at runtime
    # Autumn might use: "/home/autumn/notes/daily/{date}.md"
  time_boundaries:
    morning_cutoff: "15:00"     # before = morning, after = evening
    cat_dinner_cutoff: "17:00"  # before = breakfast, after = dinner
```

### coaching

```yaml
coaching:
  style: direct                  # direct | warm | minimal
  missed_day_policy: fire_and_forget
```

### celebrations

A list the skill rotates through. Each time a habit is logged, the next celebration in the list is used.

```yaml
celebrations:
  - "Give yourself a high five!"
  - "Sing the Zelda victory song — da-da-da-daaa!"
  - "Big WOOOHOOO!"
  - "Mental fist pump — done!"
  - "Nice work, you did it!"
```

### reminders

Each reminder defines when to fire, what message to send, which habits it covers, and follow-up behavior.

```yaml
reminders:
  - id: "morning-coach"
    schedule: "06:00"
    cadence: "daily"              # daily | mon_wed_fri | tue_thu_sat | weekdays | weekends | sunday | day_name
    message: |
      ## Morning Habits

      Here are some things you could do this morning:

      {habit_list}

      Reply with the emoji for each one as you do it.
    habits: ["cat-am", "meds-am", "teeth-am", "metamucil"]
    follow_up_delay: 60           # minutes; null = no follow-up
```

**Cadence values:**
- `"daily"` — every day
- `"weekdays"` — Monday through Friday
- `"weekends"` — Saturday, Sunday
- `"sunday"`, `"monday"`, etc. — specific day of week
- `"mon_wed_fri"` — Monday, Wednesday, Friday
- `"tue_thu_sat"` — Tuesday, Thursday, Saturday

**Message templates** support `{habit_list}` which is replaced with the rendered list of active, non-graduated habits.

### journal

What the user wants to be reminded to log, and when. These appear in coaching messages or are captured conversationally.

```yaml
journal:
  - id: "mood"
    label: "Mood"
    prompt: "How's your mood today?"
    schedule: "06:00"             # included in morning coach
    cadence: "daily"
    conversational: true          # also capture when mentioned naturally

  - id: "meals"
    label: "Meals"
    prompt: "What did you eat?"
    schedule: null                 # no scheduled reminder, conversational only
    cadence: null
    conversational: true
```

### habits

Each habit is a single behavior. Habits that happen twice a day (like meds or cat feeding) are separate entries with different `id` and `time_of_day` values.

```yaml
habits:
  - id: "cat-am"
    anchor: "After I wake up and use the bathroom"
    behavior: "I will feed the cats"
    celebration: "Cats are happy!"
    emoji: "🐱"
    emoji_variants: ["😺", "😻"]   # alternative emojis that map to this habit
    time_of_day: "morning"         # morning | afternoon | evening | any
    chain_steps:                   # optional decomposition of the habit
      - "Grab dirty dish + cat food"
      - "Set dish to soaking"
      - "Wash other dish if needed"
      - "Prepare food"
      - "Feed cat"
    graduated_to_automatic: false   # true = automatic, coaching shifts to growth
    faded: false                   # true = being skipped, coaching shifts to B=MAP troubleshooting
    active: true
```

**Key fields:**
- `graduated_to_automatic: true` — the habit is automatic. Excluded from reminder `{habit_list}`. Coaching shifts to growth/refinement.
- `faded: true` — the habit is being skipped. Shown in `{habit_list}` with a trouble indicator. Coaching shifts to B=MAP troubleshooting.
- A habit cannot have both `graduated_to_automatic` and `faded` set to true — the YAML validator rejects this.
- `emoji_variants` — alternative emojis the user might send (e.g., `😺` for `🐱`, `🪥` for `🦷`). The system maps these to the canonical habit.
- `chain_steps` — the decomposition of a multi-step habit. The first step is shown in coaching messages as the trigger.

---

## How the Master Cron Job Works

The master cron job runs **every hour** (schedule: `0 * * * *`). On each fire:

1. **Reads** `habits.yaml` from the skill directory
2. **Checks reminders** — for each reminder, is the current time within its schedule window AND does today match its cadence?
3. **Sends due reminders** — for each due reminder, builds the message from the template and delivers it
4. **Checks follow-ups** — for each reminder with `follow_up_delay` set, is the current time = schedule time + delay? If so, checks if habits have been logged today. If not, sends a gentle nudge.
5. **Does nothing** if nothing is due

### Creating the cron job

```python
cronjob(
    action="create",
    name="habit-tracking-checkin",
    schedule="0 * * * *",  # Every hour
    prompt="Run the hourly habit check-in. Read habits.yaml from the skill directory, check which reminders are due based on schedule + cadence, send those reminders, and check for follow-up nudges.",
    skills=["habit-tracking"],
    deliver="origin",
    attach_to_session=True,
)
```

---

## Coaching States

### Normal habits (default)

Appear in `{habit_list}` in reminder messages. Standard check-in treatment.

### graduated_to_automatic: true

The habit is automatic — the user does it without needing reminders.

**Coaching behavior:**
- Excluded from `{habit_list}` in reminder messages
- Still accepts emoji logs and celebrates
- When mentioned or during check-ins, offer **growth coaching**:
  - "This habit is automatic now — that's the goal working."
  - "Celebration is optional now. Keep it if it feels good, drop it if you don't need it."
  - "Want to grow it? Or use this capacity for a new tiny habit?"
  - "Is the anchor still working for you? Want to brainstorm options?"

### faded: true

The user is skipping the habit. This is data, not failure.

**Coaching behavior:**
- Appears in `{habit_list}` with a trouble indicator: `~~behavior~~ (having trouble? Let's talk about it)`
- When mentioned or during check-ins, offer **B=MAP troubleshooting**:
  - "You've been skipping this. That's data, not failure."
  - "Let's look at B=MAP. Is it a Motivation issue? An Ability issue? A Prompt issue?"
  - "If it feels hard, let's shrink it. What's the smallest version you could do?"
  - "If the anchor isn't working, let's find a better one."
  - "Want to brainstorm options together?"

---

## Celebration Rotation

When a habit is logged, the system rotates through the configured celebrations list. Each time, the next celebration in the list is used. When the end is reached, it wraps around to the start.

The celebration is sent immediately after logging, as a one-line message. This is not optional — the celebration is what wires the habit neurologically (Fogg's "shine" principle).

---

## Emoji Variant Mapping

When the user sends an emoji, the system checks:
1. Does it match a habit's `emoji` field directly?
2. Does it match any `emoji_variants` for a habit?

If a match is found, the habit is logged. Common variants:
- `😺` / `😻` → `🐱` (cat fed)
- `🪥` → `🦷` (brushed teeth)

---

## Time-of-Day Auto-Categorization

When a habit with the same emoji appears twice a day (e.g., `💊` for morning and night meds), the system disambiguates by checking the current time against `environment.time_boundaries`:

- Before `morning_cutoff` (default 15:00) → morning version
- After `morning_cutoff` → evening version
- For cat feeding: before `cat_dinner_cutoff` (default 17:00) → breakfast, after → dinner

The system does NOT ask the user which version — it uses the clock automatically.

---

## Daily Log

When `environment.daily_log.enabled` is true, habit completions and journal responses are written to the configured path. The `{date}` placeholder is replaced with the current date in YYYY-MM-DD format.

**Habit log format:**
```
- [x] 💊 I will take my morning meds (morning)
- [x] 🐱 I will feed the cats (morning)
```

**Journal log format:**
```
**Mood:** Pretty even today
**Energy:** Good after 8 hours of sleep
```

The daily log path is environment-specific. For Obsidian users it might be:
```
/mnt/obsidian-vaults/eman-mobile/Daily/{date}.md
```

For flat-file users it might be:
```
/home/autumn/notes/daily/{date}.md
```

---

## Conversational Logging

When the user mentions doing a habit in conversation (outside the check-in flow), the agent should:

1. **Detect** — scan the message for keywords from active habits' behavior and anchor text
2. **Ask** — "Did you just do **{behavior}**? {emoji} Want me to log it?"
3. **Log** — on confirmation, log to daily log and send celebration
4. **Auto-categorize** — use time-of-day boundaries to determine morning vs evening

This handles the common case where the user completes their routine before the reminder fires.

---

## Conversational Journal Logging

The agent should proactively capture mood, energy, sleep, focus, meals, and gratitude when they come up naturally in conversation. When the user mentions these:

1. Log to the daily log immediately
2. Do NOT ask "what's your mood?" — wait for it to come up naturally
3. Use the user's own words — do not paraphrase or polish

Journal prompts with `conversational: true` in the YAML are candidates for this.

---

## Setup Flow

When a user says "I want to set up habits" or similar, follow this guided flow **one question at a time**.

### Step 1: Explain Tiny Habits

> "Let's set up a habit tracking system based on BJ Fogg's Tiny Habits. The core idea is simple: start so small it feels almost too easy, attach it to something you already do, and celebrate immediately after."

### Step 2: Ask about coaching style

> "I can check in with you in different tones. Which feels right?
> - **Direct** — straightforward, no fluff
> - **Warm** — encouraging and supportive
> - **Minimal** — just the facts"

### Step 3: Ask about daily log

> "Do you want me to log your habits to a daily file? If so, where should I save it? (e.g., '/path/to/daily/{date}.md' — the {date} part gets replaced automatically)"

### Step 4: Start with 1-2 habits

> "Tiny Habits says to start with just **1 or 2 habits**. What's one tiny thing you want to make a habit?"

For each habit, ask:
- What's the **anchor**?
- What's the **tiny behavior**?
- What **celebration** feels good?
- What **emoji**?
- What time of day?

### Step 5: Create the system

1. Write the YAML file
2. Create the master cron job (hourly)
3. Confirm everything is working

---

## Managing Habits

Users manage their habits conversationally. The agent handles all YAML and cron operations.

### Add a habit
> "I want to add a new habit" → guided flow (same as Step 4)

### Remove a habit
> "Remove the vitamins habit" → confirm → remove from YAML

### List habits
> "What are my habits?" → display all active habits

### Pause / Resume
> "Pause stretching" → set `active: false`
> "Resume stretching" → set `active: true`

### Mark as graduated
> "Morning meds are automatic now" → set `graduated_to_automatic: true`

### Mark as faded
> "I keep skipping Metamucil" → set `faded: true` → offer B=MAP troubleshooting

### Change coaching style
> "Change my style to warm" → update `coaching.style`

### Add a reminder
> "I want a reminder at 8:45 AM on weekdays for PT" → create reminder entry

---

## Pitfalls

- **graduated_to_automatic and faded cannot both be true** — the YAML validator rejects this
- **Habits that happen twice a day need separate entries** — same emoji, different id and time_of_day
- **The master cron job runs hourly** — it checks which reminders are due, it doesn't send everything every hour
- **Follow-up nudges only fire if no habits have been logged** — the script checks the daily log
- **Emoji variants must be mapped** — if the user sends an unmapped emoji, it won't be recognized
- **Time-of-day boundaries are configurable** — adjust `environment.time_boundaries` if the user's schedule changes
- **Daily log path is environment-specific** — each user needs their own path configured
- **Always check the actual date before writing to the daily log** — sessions can span midnight
