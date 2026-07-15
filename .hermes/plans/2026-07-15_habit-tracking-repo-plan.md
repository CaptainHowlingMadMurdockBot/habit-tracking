# Habit Tracking — Open-Source Hermes Skill Implementation Plan

> **For Hermes:** Use subagent-driven-development to implement this plan task-by-task.

**Goal:** Build a reusable, open-source habit tracking system for Hermes Agent, starting with deployment to Autumn's Merric bot.

**Architecture:** A Python package (`habitlib`) that manages habit data (YAML), generates coaching messages, and handles dynamic cron scheduling. A Hermes skill (`habit-tracking`) that wraps the library with conversational setup, coaching, and cron management. A single master cron job that runs the daily check-in.

**Tech Stack:** Python 3.11+, PyYAML, pytest, Hermes Agent cron/skill system, GitHub (public repo)

---

## Phase 0: Project Setup & Research

### Task 0.1: Create repository structure

**Objective:** Initialize the GitHub repo with standard project scaffolding.

**Files:**
- Create: `/root/projects/habit-tracking/`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `LICENSE` (MIT)
- Create: `.gitignore`
- Create: `src/habitlib/__init__.py`
- Create: `src/habitlib/habits.py`
- Create: `src/habitlib/coach.py`
- Create: `src/habitlib/scheduler.py`
- Create: `src/habitlib/models.py`
- Create: `tests/__init__.py`
- Create: `tests/test_habits.py`
- Create: `tests/test_coach.py`
- Create: `tests/test_scheduler.py`
- Create: `docs/adr/0001-record-architecture-decisions.md`
- Create: `docs/glossary.md`
- Create: `docs/research/` (research findings go here)
- Create: `skill/SKILL.md` (the Hermes skill)
- Create: `skill/habits.yaml` (default/example config)
- Create: `.github/workflows/ci.yml`

**Step 1: Create the repo on GitHub**

```bash
cd /root/projects
mkdir habit-tracking && cd habit-tracking
gh repo create habit-tracking --public --description "Tiny Habits-based habit tracking for Hermes Agent — conversational setup, dynamic scheduling, non-judgemental coaching" --license MIT --clone
```

**Step 2: Create directory structure**

```bash
mkdir -p src/habitlib tests docs/adr docs/research skill .github/workflows
```

**Step 3: Write pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "habitlib"
version = "0.1.0"
description = "Tiny Habits-based habit tracking library for Hermes Agent"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 4: Write .gitignore**

```
__pycache__/
*.pyc
*.pyo
.env
*.egg-info/
dist/
build/
.venv/
.pytest_cache/
.coverage
```

**Step 5: Write LICENSE** — standard MIT license text.

**Step 6: Write README.md** — project overview, what it does, how to use it.

**Step 7: Write CI workflow** — `.github/workflows/ci.yml` that runs `pytest` on push/PR.

**Step 8: Write ADR 0001**

```markdown
# ADR 0001: Record Architecture Decisions

## Status
Accepted

## Context
We need a consistent way to document architectural decisions for this project.

## Decision
We will use Architecture Decision Records (ADRs) as described by Michael Nygard.

## Consequences
- Decisions are documented and reviewable
- New contributors can understand past tradeoffs
- ADRs live in `docs/adr/`
```

**Step 9: Write glossary.md**

```markdown
# Glossary

## Anchor
The existing routine that triggers a new habit (e.g., "After I pour my morning coffee").

## Behavior
The tiny action performed after the anchor (e.g., "I will take my vitamins").

## Celebration
A brief positive reinforcement immediately after the behavior (e.g., "I did it!").

## Tiny Habits
BJ Fogg's methodology: Anchor → Behavior → Celebration.

## B=MAP
Fogg's Behavior Model: Behavior = Motivation + Ability + Prompt (all three must converge).

## Dynamic Scheduling
The cron job adjusts its fire time based on when the user last engaged.

## Coaching Style
The tone of the check-in messages: direct, warm, or minimal.
```

**Step 10: Write default habits.yaml**

```yaml
# Habit tracking configuration
# Managed automatically by the habit-tracking skill.
# Do not edit manually unless you know what you're doing.

coaching_style: direct  # direct | warm | minimal
missed_day_policy: fire_and_forget  # fire_and_forget | retry_once | pause_after_3
schedule_time: "20:00"  # Initial default time (24h format)

habits:
  - id: "example"
    anchor: "After I pour my morning coffee"
    behavior: "I will take my vitamins"
    celebration: "I did it!"
    emoji: "💊"
    time_of_day: "morning"
    active: false  # Example habit, inactive by default
```

**Step 11: Write empty `__init__.py` files**

```python
# src/habitlib/__init__.py
# tests/__init__.py
```

**Step 12: Initial commit**

```bash
git add -A
git commit -m "chore: initial project scaffolding"
git push -u origin main
```

---

### Task 0.2: Incorporate BJ Fogg research

**Objective:** Save the research findings from the background subagent into `docs/research/tiny-habits-research.md`.

**Files:**
- Create: `docs/research/tiny-habits-research.md`

**Step 1:** Wait for the research subagent to complete, then copy its findings into the research file.

**Step 2:** Commit.

```bash
git add docs/research/
git commit -m "docs: add BJ Fogg Tiny Habits research"
```

---

## Phase 1: Core Library (TDD)

### Task 1.1: Create Habit data model

**Objective:** Define the `Habit` dataclass and `HabitStore` with YAML persistence.

**Files:**
- Create: `src/habitlib/models.py`
- Create: `tests/test_models.py`

**Step 1: Write failing test**

```python
# tests/test_models.py
from habitlib.models import Habit

def test_habit_creation():
    h = Habit(
        id="test",
        anchor="After I pour my coffee",
        behavior="I will take my vitamins",
        celebration="I did it!",
        emoji="💊",
        time_of_day="morning",
        active=True,
    )
    assert h.id == "test"
    assert h.anchor == "After I pour my coffee"
    assert h.behavior == "I will take my vitamins"
    assert h.celebration == "I did it!"
    assert h.emoji == "💊"
    assert h.time_of_day == "morning"
    assert h.active is True
```

Run: `pytest tests/test_models.py::test_habit_creation -v`
Expected: FAIL — `Habit` not defined

**Step 2: Write minimal implementation**

```python
# src/habitlib/models.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Habit:
    id: str
    anchor: str
    behavior: str
    celebration: str
    emoji: str
    time_of_day: str  # "morning", "afternoon", "evening", "any"
    active: bool = True
```

**Step 3: Run test to verify pass**

Run: `pytest tests/test_models.py::test_habit_creation -v`
Expected: PASS

**Step 4: Add CoachingConfig model**

Test:

```python
def test_coaching_config_defaults():
    from habitlib.models import CoachingConfig
    cfg = CoachingConfig()
    assert cfg.style == "direct"
    assert cfg.missed_day_policy == "fire_and_forget"
    assert cfg.schedule_time == "20:00"
```

Implementation:

```python
@dataclass
class CoachingConfig:
    style: str = "direct"  # "direct", "warm", "minimal"
    missed_day_policy: str = "fire_and_forget"  # "fire_and_forget", "retry_once", "pause_after_3"
    schedule_time: str = "20:00"  # HH:MM 24h format
```

**Step 5: Add HabitStoreConfig**

```python
@dataclass
class HabitStoreConfig:
    coaching: CoachingConfig = field(default_factory=CoachingConfig)
    habits: list[Habit] = field(default_factory=list)
```

**Step 6: Commit**

```bash
git add src/habitlib/models.py tests/test_models.py
git commit -m "feat: add Habit, CoachingConfig, and HabitStoreConfig models"
```

---

### Task 1.2: Implement HabitStore with YAML persistence

**Objective:** Read/write habits.yaml with validation.

**Files:**
- Create: `src/habitlib/habits.py`
- Create: `tests/test_habits.py`

**Step 1: Write failing test for loading empty store**

```python
# tests/test_habits.py
import tempfile
from pathlib import Path
from habitlib.habits import HabitStore
from habitlib.models import HabitStoreConfig

def test_load_empty_store():
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write("coaching:\n  style: direct\n  missed_day_policy: fire_and_forget\n  schedule_time: '20:00'\nhabits: []\n")
        tmp = f.name
    store = HabitStore(Path(tmp))
    config = store.load()
    assert config.coaching.style == "direct"
    assert config.coaching.missed_day_policy == "fire_and_forget"
    assert config.coaching.schedule_time == "20:00"
    assert config.habits == []
    Path(tmp).unlink()
```

Run: `pytest tests/test_habits.py::test_load_empty_store -v`
Expected: FAIL — `HabitStore` not defined

**Step 2: Write minimal implementation**

```python
# src/habitlib/habits.py
from pathlib import Path
import yaml
from habitlib.models import HabitStoreConfig, Habit, CoachingConfig

class HabitStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> HabitStoreConfig:
        if not self.path.exists():
            return HabitStoreConfig()
        with open(self.path) as f:
            data = yaml.safe_load(f) or {}
        return self._parse_config(data)

    def _parse_config(self, data: dict) -> HabitStoreConfig:
        coaching_data = data.get("coaching", {})
        coaching = CoachingConfig(
            style=coaching_data.get("style", "direct"),
            missed_day_policy=coaching_data.get("missed_day_policy", "fire_and_forget"),
            schedule_time=coaching_data.get("schedule_time", "20:00"),
        )
        habits = []
        for h in data.get("habits", []):
            habits.append(Habit(
                id=h["id"],
                anchor=h["anchor"],
                behavior=h["behavior"],
                celebration=h.get("celebration", ""),
                emoji=h.get("emoji", "✅"),
                time_of_day=h.get("time_of_day", "any"),
                active=h.get("active", True),
            ))
        return HabitStoreConfig(coaching=coaching, habits=habits)
```

**Step 3: Run test to verify pass**

Run: `pytest tests/test_habits.py::test_load_empty_store -v`
Expected: PASS

**Step 4: Write failing test for save**

```python
def test_save_and_reload():
    import tempfile
    from pathlib import Path
    from habitlib.habits import HabitStore
    from habitlib.models import Habit, HabitStoreConfig, CoachingConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "habits.yaml"
        store = HabitStore(path)

        config = HabitStoreConfig(
            coaching=CoachingConfig(style="warm"),
            habits=[
                Habit(id="h1", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning"),
            ]
        )
        store.save(config)

        # Reload
        store2 = HabitStore(path)
        loaded = store2.load()
        assert loaded.coaching.style == "warm"
        assert len(loaded.habits) == 1
        assert loaded.habits[0].id == "h1"
        assert loaded.habits[0].anchor == "After coffee"
```

Run: `pytest tests/test_habits.py::test_save_and_reload -v`
Expected: FAIL — `save` not implemented

**Step 5: Implement save**

```python
def save(self, config: HabitStoreConfig):
    data = {
        "coaching": {
            "style": config.coaching.style,
            "missed_day_policy": config.coaching.missed_day_policy,
            "schedule_time": config.coaching.schedule_time,
        },
        "habits": [
            {
                "id": h.id,
                "anchor": h.anchor,
                "behavior": h.behavior,
                "celebration": h.celebration,
                "emoji": h.emoji,
                "time_of_day": h.time_of_day,
                "active": h.active,
            }
            for h in config.habits
        ],
    }
    self.path.parent.mkdir(parents=True, exist_ok=True)
    with open(self.path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

**Step 6: Run test to verify pass**

Run: `pytest tests/test_habits.py::test_save_and_reload -v`
Expected: PASS

**Step 7: Write failing test for add_habit**

```python
def test_add_habit():
    import tempfile
    from pathlib import Path
    from habitlib.habits import HabitStore
    from habitlib.models import Habit

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "habits.yaml"
        store = HabitStore(path)

        h = Habit(id="h1", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning")
        store.add_habit(h)

        loaded = store.load()
        assert len(loaded.habits) == 1
        assert loaded.habits[0].id == "h1"
```

Run: `pytest tests/test_habits.py::test_add_habit -v`
Expected: FAIL — `add_habit` not implemented

**Step 8: Implement add_habit and remove_habit**

```python
def add_habit(self, habit: Habit):
    config = self.load()
    # Check for duplicate id
    if any(h.id == habit.id for h in config.habits):
        raise ValueError(f"Habit with id '{habit.id}' already exists")
    config.habits.append(habit)
    self.save(config)

def remove_habit(self, habit_id: str):
    config = self.load()
    config.habits = [h for h in config.habits if h.id != habit_id]
    self.save(config)
```

**Step 9: Run tests to verify pass**

Run: `pytest tests/test_habits.py -v`
Expected: 3 passed

**Step 10: Commit**

```bash
git add src/habitlib/habits.py tests/test_habits.py
git commit -m "feat: implement HabitStore with YAML persistence"
```

---

### Task 1.3: Implement Coach engine

**Objective:** Generate coaching messages based on habit data and coaching style. Also detect when the user mentions habit-related activity in conversation and prompt them to log.

**Files:**
- Create: `src/habitlib/coach.py`
- Create: `tests/test_coach.py`

**Step 1: Write failing test for direct style check-in**

```python
# tests/test_coach.py
from habitlib.coach import Coach
from habitlib.models import Habit, CoachingConfig

def test_direct_checkin_one_habit():
    coach = Coach(CoachingConfig(style="direct"))
    habits = [
        Habit(id="v", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning"),
    ]
    msg = coach.checkin(habits)
    assert "💊" in msg
    assert "Vitamins" in msg
    assert "After coffee" in msg
    assert "1 habit" in msg or "1 of 1" in msg
```

Run: `pytest tests/test_coach.py::test_direct_checkin_one_habit -v`
Expected: FAIL — `Coach` not defined

**Step 2: Write minimal implementation**

```python
# src/habitlib/coach.py
from habitlib.models import Habit, CoachingConfig

class Coach:
    def __init__(self, config: CoachingConfig):
        self.config = config

    def checkin(self, habits: list[Habit]) -> str:
        active = [h for h in habits if h.active]
        if not active:
            return "No active habits to check in on. Add one with 'I want to start a new habit!'"

        lines = []
        for h in active:
            lines.append(f"{h.emoji} **{h.behavior}** — {h.anchor}")

        total = len(active)
        header = f"## Daily Check-in\n\n"
        body = "\n".join(lines)
        footer = f"\n\nThat's **{total}** habit{'s' if total > 1 else ''} today. How did it go? Reply with what you did!"

        if self.config.style == "direct":
            footer += "\n\nNo worries if you missed one — tomorrow's a fresh start."

        return header + body + footer
```

**Step 3: Run test to verify pass**

Run: `pytest tests/test_coach.py::test_direct_checkin_one_habit -v`
Expected: PASS

**Step 4: Write failing test for warm style**

```python
def test_warm_checkin():
    coach = Coach(CoachingConfig(style="warm"))
    habits = [
        Habit(id="v", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning"),
    ]
    msg = coach.checkin(habits)
    assert "💊" in msg
    assert "proud" in msg or "great" in msg or "you've got" in msg
```

Run: `pytest tests/test_coach.py::test_warm_checkin -v`
Expected: FAIL — warm style not differentiated

**Step 5: Implement style differentiation**

```python
def checkin(self, habits: list[Habit]) -> str:
    active = [h for h in habits if h.active]
    if not active:
        return "No active habits to check in on. Add one with 'I want to start a new habit!'"

    lines = []
    for h in active:
        lines.append(f"{h.emoji} **{h.behavior}** — {h.anchor}")

    total = len(active)
    header = f"## Daily Check-in\n\n"
    body = "\n".join(lines)
    footer = f"\n\nThat's **{total}** habit{'s' if total > 1 else ''} today."

    if self.config.style == "direct":
        footer += " How did it go? Reply with what you did!\n\nNo worries if you missed one — tomorrow's a fresh start."
    elif self.config.style == "warm":
        footer += " How are you feeling about it? I'm proud of you for showing up.\n\nAnd if today wasn't your day — that's okay. You're building something that lasts."
    elif self.config.style == "minimal":
        footer += " Reply with your update."

    return header + body + footer
```

**Step 6: Run tests to verify pass**

Run: `pytest tests/test_coach.py -v`
Expected: 2 passed

**Step 7: Write failing test for celebration message**

```python
def test_celebration_direct():
    coach = Coach(CoachingConfig(style="direct"))
    msg = coach.celebrate("Vitamins")
    assert "Vitamins" in msg
    assert "Nice" in msg or "done" in msg or "great" in msg
```

Run: `pytest tests/test_coach.py::test_celebration_direct -v`
Expected: FAIL — `celebrate` not implemented

**Step 8: Implement celebrate**

```python
def celebrate(self, behavior: str) -> str:
    if self.config.style == "direct":
        return f"✅ **{behavior}** — logged. Nice work."
    elif self.config.style == "warm":
        return f"🌟 **{behavior}** — that's awesome! You're building something real."
    elif self.config.style == "minimal":
        return f"✅ {behavior}"
    return f"✅ {behavior}"
```

**Step 9: Run tests to verify pass**

Run: `pytest tests/test_coach.py -v`
Expected: 3 passed

**Step 10: Write failing test for conversational logging trigger**

```python
def test_detect_habit_mention():
    coach = Coach(CoachingConfig(style="direct"))
    habits = [
        Habit(id="v", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning"),
        Habit(id="s", anchor="After lunch", behavior="Stretch", celebration="Good!", emoji="🧘", time_of_day="afternoon"),
    ]
    # User mentions doing a habit
    result = coach.detect_habit_mention("I just took my vitamins with my coffee", habits)
    assert result is not None
    assert result.id == "v"

def test_detect_no_habit_mention():
    coach = Coach(CoachingConfig(style="direct"))
    habits = [
        Habit(id="v", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning"),
    ]
    result = coach.detect_habit_mention("I'm going to the store", habits)
    assert result is None
```

Run: `pytest tests/test_coach.py::test_detect_habit_mention -v`
Expected: FAIL — `detect_habit_mention` not implemented

**Step 11: Implement detect_habit_mention**

```python
def detect_habit_mention(self, message: str, habits: list[Habit]) -> Habit | None:
    """Check if a user message mentions doing a habit. Returns the matched Habit or None."""
    msg_lower = message.lower()
    for h in habits:
        if not h.active:
            continue
        # Check if the behavior or anchor keywords appear in the message
        behavior_words = h.behavior.lower().split()
        anchor_words = h.anchor.lower().split()
        # Match if any significant word from behavior or anchor appears
        for word in behavior_words + anchor_words:
            if len(word) > 3 and word in msg_lower:
                return h
    return None
```

**Step 12: Run tests to verify pass**

Run: `pytest tests/test_coach.py -v`
Expected: 5 passed

**Step 13: Write failing test for logging prompt**

```python
def test_logging_prompt():
    coach = Coach(CoachingConfig(style="direct"))
    msg = coach.logging_prompt("Vitamins", "💊")
    assert "💊" in msg
    assert "Vitamins" in msg
    assert "log" in msg.lower() or "done" in msg.lower()
```

Run: `pytest tests/test_coach.py::test_logging_prompt -v`
Expected: FAIL — `logging_prompt` not implemented

**Step 14: Implement logging_prompt**

```python
def logging_prompt(self, behavior: str, emoji: str) -> str:
    return f"Did you just do **{behavior}**? {emoji} Want me to log it?"
```

**Step 15: Run tests to verify pass**

Run: `pytest tests/test_coach.py -v`
Expected: 6 passed

**Step 16: Commit**

```bash
git add src/habitlib/coach.py tests/test_coach.py
git commit -m "feat: implement Coach with habit mention detection and logging prompts"
```

**Files:**
- Create: `src/habitlib/coach.py`
- Create: `tests/test_coach.py`

**Step 1: Write failing test for direct style check-in**

```python
# tests/test_coach.py
from habitlib.coach import Coach
from habitlib.models import Habit, CoachingConfig

def test_direct_checkin_one_habit():
    coach = Coach(CoachingConfig(style="direct"))
    habits = [
        Habit(id="v", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning"),
    ]
    msg = coach.checkin(habits)
    assert "💊" in msg
    assert "Vitamins" in msg
    assert "After coffee" in msg
    assert "1 habit" in msg or "1 of 1" in msg
```

Run: `pytest tests/test_coach.py::test_direct_checkin_one_habit -v`
Expected: FAIL — `Coach` not defined

**Step 2: Write minimal implementation**

```python
# src/habitlib/coach.py
from habitlib.models import Habit, CoachingConfig

class Coach:
    def __init__(self, config: CoachingConfig):
        self.config = config

    def checkin(self, habits: list[Habit]) -> str:
        active = [h for h in habits if h.active]
        if not active:
            return "No active habits to check in on. Add one with 'I want to start a new habit!'"

        lines = []
        for h in active:
            lines.append(f"{h.emoji} **{h.behavior}** — {h.anchor}")

        total = len(active)
        header = f"## Daily Check-in\n\n"
        body = "\n".join(lines)
        footer = f"\n\nThat's **{total}** habit{'s' if total > 1 else ''} today. How did it go? Reply with what you did!"

        if self.config.style == "direct":
            footer += "\n\nNo worries if you missed one — tomorrow's a fresh start."

        return header + body + footer
```

**Step 3: Run test to verify pass**

Run: `pytest tests/test_coach.py::test_direct_checkin_one_habit -v`
Expected: PASS

**Step 4: Write failing test for warm style**

```python
def test_warm_checkin():
    coach = Coach(CoachingConfig(style="warm"))
    habits = [
        Habit(id="v", anchor="After coffee", behavior="Vitamins", celebration="Nice!", emoji="💊", time_of_day="morning"),
    ]
    msg = coach.checkin(habits)
    assert "💊" in msg
    assert "proud" in msg or "great" in msg or "you've got" in msg
```

Run: `pytest tests/test_coach.py::test_warm_checkin -v`
Expected: FAIL — warm style not differentiated

**Step 5: Implement style differentiation**

```python
def checkin(self, habits: list[Habit]) -> str:
    active = [h for h in habits if h.active]
    if not active:
        return "No active habits to check in on. Add one with 'I want to start a new habit!'"

    lines = []
    for h in active:
        lines.append(f"{h.emoji} **{h.behavior}** — {h.anchor}")

    total = len(active)
    header = f"## Daily Check-in\n\n"
    body = "\n".join(lines)
    footer = f"\n\nThat's **{total}** habit{'s' if total > 1 else ''} today."

    if self.config.style == "direct":
        footer += " How did it go? Reply with what you did!\n\nNo worries if you missed one — tomorrow's a fresh start."
    elif self.config.style == "warm":
        footer += " How are you feeling about it? I'm proud of you for showing up.\n\nAnd if today wasn't your day — that's okay. You're building something that lasts."
    elif self.config.style == "minimal":
        footer += " Reply with your update."

    return header + body + footer
```

**Step 6: Run tests to verify pass**

Run: `pytest tests/test_coach.py -v`
Expected: 2 passed

**Step 7: Write failing test for celebration message**

```python
def test_celebration_direct():
    coach = Coach(CoachingConfig(style="direct"))
    msg = coach.celebrate("Vitamins")
    assert "Vitamins" in msg
    assert "Nice" in msg or "done" in msg or "great" in msg
```

Run: `pytest tests/test_coach.py::test_celebration_direct -v`
Expected: FAIL — `celebrate` not implemented

**Step 8: Implement celebrate**

```python
def celebrate(self, behavior: str) -> str:
    if self.config.style == "direct":
        return f"✅ **{behavior}** — logged. Nice work."
    elif self.config.style == "warm":
        return f"🌟 **{behavior}** — that's awesome! You're building something real."
    elif self.config.style == "minimal":
        return f"✅ {behavior}"
    return f"✅ {behavior}"
```

**Step 9: Run tests to verify pass**

Run: `pytest tests/test_coach.py -v`
Expected: 3 passed

**Step 10: Commit**

```bash
git add src/habitlib/coach.py tests/test_coach.py
git commit -m "feat: implement Coach with direct, warm, and minimal styles"
```

---

### Task 1.4: Implement Scheduler for dynamic cron scheduling

**Objective:** Handle the dynamic schedule adjustment logic.

**Files:**
- Create: `src/habitlib/scheduler.py`
- Create: `tests/test_scheduler.py`

**Step 1: Write failing test for time conversion**

```python
# tests/test_scheduler.py
from habitlib.scheduler import Scheduler

def test_reply_time_to_cron():
    # If she replies at 11:47 PM, next fire should be 47 23 * * *
    cron = Scheduler.reply_time_to_cron("23:47")
    assert cron == "47 23 * * *"

def test_reply_time_to_cron_midnight():
    cron = Scheduler.reply_time_to_cron("00:15")
    assert cron == "15 0 * * *"
```

Run: `pytest tests/test_scheduler.py -v`
Expected: FAIL — `Scheduler` not defined

**Step 2: Write minimal implementation**

```python
# src/habitlib/scheduler.py
from datetime import datetime

class Scheduler:
    @staticmethod
    def reply_time_to_cron(time_str: str) -> str:
        """Convert HH:MM to cron expression (minute hour * * *)."""
        parts = time_str.split(":")
        minute = int(parts[0]) if len(parts) == 2 else 0
        hour = int(parts[1]) if len(parts) == 2 else int(parts[0])
        return f"{minute} {hour} * * *"

    @staticmethod
    def now_as_hhmm() -> str:
        now = datetime.now()
        return f"{now.hour:02d}:{now.minute:02d}"
```

Wait — I got the split backwards. Let me fix:

```python
@staticmethod
def reply_time_to_cron(time_str: str) -> str:
    """Convert HH:MM to cron expression (minute hour * * *)."""
    parts = time_str.split(":")
    hour = int(parts[0])
    minute = int(parts[1])
    return f"{minute} {hour} * * *"
```

**Step 3: Run test to verify pass**

Run: `pytest tests/test_scheduler.py -v`
Expected: PASS

**Step 4: Write failing test for schedule update message**

```python
def test_schedule_update_message():
    msg = Scheduler.schedule_update_message("22:15", "22:15")
    assert "same time" in msg or "22:15" in msg

def test_schedule_update_message_changed():
    msg = Scheduler.schedule_update_message("20:00", "23:47")
    assert "23:47" in msg
    assert "shifted" in msg or "adjusted" in msg or "tomorrow" in msg
```

Run: `pytest tests/test_scheduler.py::test_schedule_update_message -v`
Expected: FAIL — `schedule_update_message` not implemented

**Step 5: Implement schedule_update_message**

```python
@staticmethod
def schedule_update_message(old_time: str, new_time: str) -> str:
    if old_time == new_time:
        return f"I'll check in with you at the same time tomorrow ({new_time})."
    return f"I've adjusted tomorrow's check-in to {new_time} to match when you're free."
```

**Step 6: Run tests to verify pass**

Run: `pytest tests/test_scheduler.py -v`
Expected: 4 passed

**Step 7: Commit**

```bash
git add src/habitlib/scheduler.py tests/test_scheduler.py
git commit -m "feat: implement Scheduler for dynamic cron scheduling"
```

---

## Phase 2: Hermes Skill

### Task 2.1: Write the SKILL.md

**Objective:** Create the Hermes skill that agents load to provide habit tracking.

**Files:**
- Create: `skill/SKILL.md`

**Step 1: Write SKILL.md**

The skill document should contain:

1. **Frontmatter** — name, description, version, author, license
2. **Overview** — what this skill does
3. **Tiny Habits Methodology** — with research citations from `docs/research/tiny-habits-research.md`
   - B=MAP (Behavior = Motivation + Ability + Prompt)
   - Anchor → Behavior → Celebration formula
   - Start small (1-2 habits)
   - Shrink the habit technique
   - Celebration as skill, not reward
4. **Setup Flow** — guided conversation for new users
   - Explain Tiny Habits philosophy
   - Ask about coaching style (direct/warm/minimal)
   - Ask about missed day policy
   - Ask about initial time preference
   - Start with 1-2 habits, one question at a time
   - Create the YAML file
   - Create the master cron job
5. **Daily Check-in** — how the cron job works
   - Reads habits.yaml
   - Generates coaching message
   - Delivers to user
   - On reply: logs completion, celebrates, updates schedule
6. **Managing Habits** — conversational commands
   - "Add a habit" → guided flow
   - "Remove [habit]" → confirm then remove
   - "List my habits" → show all
   - "Change my coaching style" → update config
   - "Pause [habit]" → set active=false
   - "Resume [habit]" → set active=true
7. **Dynamic Scheduling** — how the cron adjusts
   - On reply, extract timestamp
   - Calculate new cron expression
   - Update the cron job
   - Inform user of next check-in time
8. **Conversational Logging** — when the user mentions doing a habit in conversation
   - Detect keywords from active habits in user messages
   - If match found, ask: "Did you just do [behavior]? Want me to log it?"
   - On confirmation, log it and celebrate
   - This handles the case where the user talks about their routine before the reminder fires
9. **Non-judgemental Coaching** — guidelines
   - Never guilt or shame
   - "Could" not "should"
   - Celebrate every completion
   - Missed days are data, not failure
   - Encourage shrinking the habit, not quitting
9. **Pitfalls** — common issues and how to handle them
   - User tries to add too many habits at once → redirect to start small
   - User misses multiple days → gentle check-in, offer to shrink
   - User wants to delete cron jobs → explain the master cron system
   - YAML file corrupted → recreate from defaults

**Step 2: Commit**

```bash
git add skill/SKILL.md
git commit -m "feat: add habit-tracking Hermes skill"
```

---

### Task 2.2: Write the setup script

**Objective:** Create a Python script that the skill can use for initial setup.

**Files:**
- Create: `skill/scripts/setup.py`

This script handles:
- Creating the habits.yaml with user's choices
- Creating the master cron job
- Validating the setup

**Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Setup script for habit-tracking skill. Called by the agent during onboarding."""

import sys
import json
from pathlib import Path

# The agent passes setup choices as JSON via stdin
# {
#   "coaching_style": "direct",
#   "missed_day_policy": "fire_and_forget",
#   "schedule_time": "20:00",
#   "habits": [
#     {"id": "v", "anchor": "...", "behavior": "...", "celebration": "...", "emoji": "...", "time_of_day": "morning"}
#   ],
#   "skill_dir": "/home/autumn/.hermes/skills/habit-tracking"
# }

def main():
    data = json.load(sys.stdin)
    skill_dir = Path(data["skill_dir"])
    habits_path = skill_dir / "habits.yaml"

    # Build the YAML
    config = {
        "coaching": {
            "style": data["coaching_style"],
            "missed_day_policy": data["missed_day_policy"],
            "schedule_time": data["schedule_time"],
        },
        "habits": [
            {
                "id": h["id"],
                "anchor": h["anchor"],
                "behavior": h["behavior"],
                "celebration": h.get("celebration", ""),
                "emoji": h.get("emoji", "✅"),
                "time_of_day": h.get("time_of_day", "any"),
                "active": True,
            }
            for h in data["habits"]
        ],
    }

    import yaml
    habits_path.parent.mkdir(parents=True, exist_ok=True)
    with open(habits_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(json.dumps({"status": "ok", "path": str(habits_path), "habit_count": len(data["habits"])}))

if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add skill/scripts/setup.py
git commit -m "feat: add setup script for habit-tracking skill"
```

---

## Phase 3: Deployment to Autumn

### Task 3.1: Clean up Autumn's existing cron jobs

**Objective:** Remove the broken dishwasher reminder and any other stale cron jobs from Autumn's default profile.

**Files:**
- Modify: Autumn's cron jobs (via `cronjob` tool on her profile)

**Step 1:** List Autumn's cron jobs to see what's there.

**Step 2:** Remove the dishwasher reminder and any other stale jobs.

**Step 3:** Confirm removal with Autumn.

---

### Task 3.2: Install the skill on Autumn's profile

**Objective:** Copy the skill to `/home/autumn/.hermes/skills/habit-tracking/`.

**Files:**
- Create: `/home/autumn/.hermes/skills/habit-tracking/SKILL.md`
- Create: `/home/autumn/.hermes/skills/habit-tracking/habits.yaml`
- Create: `/home/autumn/.hermes/skills/habit-tracking/scripts/setup.py`

**Step 1:** Copy the skill files.

```bash
mkdir -p /home/autumn/.hermes/skills/habit-tracking/scripts
cp /root/projects/habit-tracking/skill/SKILL.md /home/autumn/.hermes/skills/habit-tracking/
cp /root/projects/habit-tracking/skill/habits.yaml /home/autumn/.hermes/skills/habit-tracking/
cp /root/projects/habit-tracking/skill/scripts/setup.py /home/autumn/.hermes/skills/habit-tracking/scripts/
chown -R autumn:autumn /home/autumn/.hermes/skills/habit-tracking/
```

**Step 2:** Verify the skill is loadable.

---

### Task 3.3: Walk through setup with Autumn

**Objective:** Guide Autumn through the initial setup conversationally.

The agent (on her Merric bot) loads the skill and walks her through:
1. What Tiny Habits is and why it works
2. Choosing a coaching style
3. Choosing a missed-day policy
4. Setting an initial check-in time
5. Starting with 1-2 habits
6. Creating the master cron job

---

## Phase 4: Polish & Documentation

### Task 4.1: Write comprehensive README

**Objective:** Make the repo welcoming and useful for other Hermes users.

**Contents:**
- What is this?
- How it works (architecture overview)
- Quick start
- Configuration reference
- Coaching styles explained
- Dynamic scheduling explained
- Development (how to contribute, run tests)
- License

### Task 4.2: Add ADRs for key decisions

- ADR 0002: Dynamic scheduling approach
- ADR 0003: Single master cron job vs per-habit cron jobs
- ADR 0004: YAML-based habit storage
- ADR 0005: Coaching style configuration

### Task 4.3: Final review and push

- Run full test suite
- Verify CI passes
- Tag v0.1.0 release
- Push to GitHub

---

## Verification

After all tasks complete:

- [ ] `pytest tests/ -v` — all tests pass
- [ ] `gh repo view CaptainHowlingMadMurdockBot/habit-tracking` — repo exists and is public
- [ ] Skill loads on Autumn's profile: `hermes skill list` shows `habit-tracking`
- [ ] habits.yaml exists at `/home/autumn/.hermes/skills/habit-tracking/habits.yaml`
- [ ] Master cron job exists and delivers to Autumn's Merric bot
- [ ] Old dishwasher cron job is removed
