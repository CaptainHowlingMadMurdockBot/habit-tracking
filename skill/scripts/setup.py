#!/usr/bin/env python3
"""Setup script for habit-tracking skill.

Called by the agent during onboarding. Receives setup choices via JSON on stdin
and writes the initial habits.yaml file.

Usage:
    echo '{"coaching_style": "direct", ...}' | python3 setup.py
"""

import json
import sys
from pathlib import Path


def main():
    data = json.load(sys.stdin)
    skill_dir = Path(data["skill_dir"])
    habits_path = skill_dir / "habits.yaml"

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

    result = {
        "status": "ok",
        "path": str(habits_path),
        "habit_count": len(data["habits"]),
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
