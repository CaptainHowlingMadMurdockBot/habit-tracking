---
name: habit-tracking
description: "Tiny Habits-based habit tracking — conversational setup, dynamic scheduling, non-judgemental coaching. Inspired by BJ Fogg's research."
version: 0.1.0
author: Hermes Agent (inspired by BJ Fogg's Tiny Habits methodology)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [habits, coaching, tiny-habits, productivity, wellness]
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

This skill provides a complete habit tracking system built on BJ Fogg's Tiny Habits methodology. It uses a **single master cron job** that delivers a daily check-in, dynamically adjusts to your schedule, and coaches you in your chosen style.

**Core principles:**
- **Start small** — 1-2 habits at a time, tiny enough to feel easy
- **Anchor → Behavior → Celebration** — the Tiny Habits formula
- **Non-judgemental** — "could" not "should", missed days are data not failure
- **Adaptive** — the check-in time shifts to match when you actually engage
- **Conversational** — mention doing a habit and the bot offers to log it

---

## Tiny Habits Methodology

### B=MAP (Fogg Behavior Model)

Behavior occurs when **Motivation**, **Ability**, and **Prompt** converge simultaneously:

- **Motivation** — how much you want to do the behavior
- **Ability** — how easy the behavior is (the "Simplicity Factors": time, money, effort, brain cycles, routine)
- **Prompt** — the trigger that tells you to act

Tiny Habits works by maximizing **Ability** (making the behavior tiny) and using a reliable **Anchor** as the Prompt, reducing the need for strong Motivation.

*Source: [bjfogg.com](https://www.bjfogg.com), Tiny Habits book Ch. 2*

### The Recipe: Anchor → Behavior → Celebration

```
After I [ANCHOR], I will [TINY BEHAVIOR], then I will [CELEBRATE].
```

- **Anchor** — an existing routine that reliably happens (e.g., "After I pour my morning coffee")
- **Tiny Behavior** — a behavior so small it takes <30 seconds (e.g., "I will take my vitamins")
- **Celebration** — a brief positive emotion or gesture immediately after (e.g., "I did it!")

The celebration creates a neural "shine" that wires the habit loop. Even a 1-second celebration dramatically increases habit formation speed.

*Source: [tinyhabits.com/tell-me-more3](https://tinyhabits.com/tell-me-more3/), Tiny Habits book Ch. 5*

### Start Small

**Start with only 1-2 habits.** Research shows:

- **84%** of participants who started with a 1-second behavior maintained it after 6 weeks, vs **38%** for a 30-second behavior (Stanford Behavior Design Lab, 2018-19)
- **71%** success rate with Tiny Habits formula vs **27%** for traditional goal-setting (Fogg et al., 2020, field trial with 1,200 users)
- **3x increase** in habit retention when celebration is added immediately (Fogg, 2021, *Behavior Design* meta-analysis)

*Source: [bjfogg.com](https://www.bjfogg.com), Tiny Habits book Ch. 4*

### Shrink the Habit

If a habit feels hard, **shrink it**:
1. Reduce to an even smaller action (e.g., "floss one tooth" → "touch the floss")
2. Keep the same anchor and celebration
3. Once automatic, gradually expand

### Missed Days

Missed days are **data, not failure**. Simply repeat the recipe the next day. No apology, no reprimand. The system never guilts you.

---

## Setup Flow

When a user says "I want to set up habits" or similar, follow this guided flow **one question at a time**. Teach the Tiny Habits philosophy as you go.

### Step 1: Explain Tiny Habits

> "Let's set up a habit tracking system based on BJ Fogg's Tiny Habits. The core idea is simple: start so small it feels almost too easy, attach it to something you already do, and celebrate immediately after. This works because we're designing for **ability** — making the behavior easy — rather than relying on motivation, which comes and goes."

### Step 2: Ask about coaching style

> "I can check in with you in different tones. Which feels right?
> - **Direct** — straightforward, no fluff. 'How did it go? Reply with what you did! No worries if you missed one — tomorrow's a fresh start.'
> - **Warm** — encouraging and supportive. 'How are you feeling about it? I'm proud of you for showing up.'
> - **Minimal** — just the facts. 'Reply with your update.'
>
> I'd recommend starting with **direct** — it's the clearest. You can change anytime."

### Step 3: Ask about missed day policy

> "If you don't reply for a while, how should I handle it?
> - **Fire and forget** — I send one message per day, no follow-up. The schedule only shifts when you engage.
> - **Retry once** — if you don't reply within a few hours, I'll send one gentle nudge.
> - **Pause after 3** — if I don't hear from you for 3 days, I'll pause and ask if you want to keep going.
>
> I'd recommend **fire and forget** — it's the least pressure."

### Step 4: Ask about initial check-in time

> "What time of day should I check in? You can change this later — the system will actually adjust to when you naturally reply. For now, what works?"

### Step 5: Start with 1-2 habits (Tiny Habits principle)

> "Tiny Habits says to start with just **1 or 2 habits** — small enough that they feel easy. You can always add more later once these become automatic. What's one tiny thing you want to make a habit?"

For each habit, ask:

> "What's the **anchor** — an existing routine it will follow? (e.g., 'After I pour my morning coffee')"
>
> "What's the **tiny behavior**? Keep it under 30 seconds. (e.g., 'I will take my vitamins')"
>
> "What **celebration** feels good to you? (e.g., 'I did it!', a fist pump, 'Nice!')"
>
> "What **emoji** should represent this habit?"
>
> "What time of day? (morning / afternoon / evening / any)"

**If they try to add more than 2 habits:** gently redirect.

> "Tiny Habits research shows that starting with more than 2 habits dramatically lowers success rates. Let's nail these first, then add more in a week or two. Which 2 are most important to you right now?"

### Step 6: Create the system

Once setup is complete:

1. Write the habits to `habits.yaml` in the skill directory
2. Create the master cron job (see [Cron Job Setup](#cron-job-setup))
3. Confirm everything is working

---

## Daily Check-in

The master cron job fires once per day. When it fires, the agent:

1. **Reads** `habits.yaml` from the skill directory
2. **Generates** a check-in message using the configured coaching style
3. **Delivers** the message to the user

### Check-in message format

```
## Daily Check-in

💊 I will take my vitamins — After I pour my morning coffee
🧘 I will stretch — After lunch

That's 2 habits today. How did it go? Reply with what you did!

No worries if you missed one — tomorrow's a fresh start.
```

### After the user replies

1. **Log the completion** — acknowledge what they did
2. **Celebrate** — send a celebration message in their style
3. **Update the schedule** — extract the reply timestamp, calculate the new cron time, update the cron job
4. **Inform** — tell them when tomorrow's check-in will be

### If the user mentions doing a habit in conversation

The agent should **detect** when the user talks about their habits outside of the check-in flow. For example:

> User: "I just took my vitamins with my coffee"
> Agent: "Did you just do **I will take my vitamins**? 💊 Want me to log it?"

Use the `detect_habit_mention` method: scan the user's message for keywords from active habits' behavior and anchor text. If a match is found, ask if they want to log it.

This handles the common case where the user completes their routine before the reminder fires.

---

## Managing Habits

Users manage their habits conversationally. The agent handles all YAML and cron operations.

### Add a habit

> User: "I want to add a new habit"
> Agent: "Great! What's the anchor — an existing routine it will follow?"

Follow the same questions as Step 5 of setup. After collecting all details, add to `habits.yaml` and confirm.

### Remove a habit

> User: "Remove the vitamins habit"
> Agent: "Remove **I will take my vitamins** (💊)? [confirm]"
> User: "Yes"
> Agent: Removes from `habits.yaml`. "Done! Removed **I will take my vitamins**."

### List habits

> User: "What are my habits?"
> Agent: Reads `habits.yaml` and displays all active habits with their anchors and emojis.

### Pause / Resume

> User: "Pause the stretching habit"
> Agent: Sets `active: false` in `habits.yaml`. "Paused **I will stretch**. It won't appear in check-ins until you resume it."

> User: "Resume stretching"
> Agent: Sets `active: true`. "Resumed **I will stretch**! It'll be in tonight's check-in."

### Change coaching style

> User: "Change my style to warm"
> Agent: Updates `coaching.style` in `habits.yaml`. "Done! I'll use a warmer tone from now on."

### Change missed day policy

> User: "If I don't reply, try again later"
> Agent: Updates `coaching.missed_day_policy` to `retry_once`. "Got it. If you don't reply within a few hours, I'll send one gentle nudge."

---

## Dynamic Scheduling

The system adjusts its check-in time based on when the user actually engages.

**How it works:**
1. The cron job fires at the scheduled time
2. The user replies at some time (e.g., 11:47 PM)
3. The agent extracts the reply timestamp
4. The agent calculates a new cron expression: `47 23 * * *`
5. The agent updates the cron job with the new schedule
6. The agent tells the user: "I've adjusted tomorrow's check-in to 23:47 to match when you're free."

**If the user replies at the same time as before:** "I'll check in with you at the same time tomorrow (23:47)."

**If the user doesn't reply:** the schedule stays the same. It only shifts when they engage.

---

## Cron Job Setup

The system uses a **single master cron job** that handles all habits. This avoids the complexity of managing multiple cron jobs.

### Creating the cron job

```python
# The agent creates one cron job during setup
cronjob(
    action="create",
    name="habit-tracking-checkin",
    schedule="0 20 * * *",  # Initial time, adjusted dynamically
    prompt="Run the daily habit check-in. Read habits.yaml from the skill directory, generate the check-in message using the configured coaching style, and deliver it to the user.",
    skills=["habit-tracking"],
    deliver="origin",
    attach_to_session=True,  # So replies continue the conversation
)
```

### Updating the cron job (dynamic scheduling)

```python
cronjob(
    action="update",
    job_id="<job_id>",
    schedule="47 23 * * *",  # New time based on user's reply
)
```

### Removing the cron job

```python
cronjob(action="list")  # Find the job_id
cronjob(action="remove", job_id="<job_id>")
```

---

## Non-judgemental Coaching Guidelines

The agent should follow these principles in all habit-related interactions:

1. **"Could" not "should"** — "You could try..." not "You should..."
2. **Celebrate every completion** — no matter how small
3. **Missed days are data** — "No worries if you missed one — tomorrow's a fresh start."
4. **Encourage shrinking, not quitting** — if a habit feels hard, suggest making it smaller
5. **Never guilt or shame** — no "you didn't do it yesterday" without a neutral framing
6. **Start small, stay small** — redirect if they try to add too many habits at once
7. **Autonomy** — the user chooses their habits, style, and schedule

---

## Pitfalls

### User tries to add too many habits at once
Redirect gently: "Tiny Habits research shows that starting with more than 2 habits dramatically lowers success rates. Let's nail these first."

### User misses multiple days
The system handles this based on the configured `missed_day_policy`. If `fire_and_forget`, just send the next check-in as normal. If `pause_after_3`, after 3 missed days send: "I noticed I haven't heard from you in a few days. Would you like to pause your habits, adjust them, or keep going?"

### User wants to delete cron jobs themselves
Explain: "There's one master cron job that handles all your habits. I can manage it for you — just tell me what you want to change."

### YAML file corrupted
If `habits.yaml` fails to parse, recreate from defaults and ask the user to confirm their habits.

### User talks about habits outside check-in
Use `detect_habit_mention` to check if they're describing a habit they've done. If so, offer to log it. This prevents the frustration of completing a habit, mentioning it, and the agent not connecting the dots.

---

## File Structure

```
~/.hermes/skills/habit-tracking/
├── SKILL.md              # This file
├── habits.yaml           # Persistent habit data (managed by the agent)
└── scripts/
    └── setup.py          # Setup script for initial configuration
```

### habits.yaml format

```yaml
coaching:
  style: direct           # direct | warm | minimal
  missed_day_policy: fire_and_forget  # fire_and_forget | retry_once | pause_after_3
  schedule_time: "20:00"  # HH:MM 24h format

habits:
  - id: "vitamins"
    anchor: "After I pour my morning coffee"
    behavior: "I will take my vitamins"
    celebration: "I did it!"
    emoji: "💊"
    time_of_day: "morning"
    active: true
```
