# ADR 0004: YAML-Based Habit Storage

## Status
Accepted

## Context
We needed a persistent storage format for habit data that is both machine-readable and human-editable.

## Decision
Store habit data in YAML format. The file lives in the skill directory alongside SKILL.md. The agent reads and writes it programmatically, but a user can inspect or edit it manually if needed.

## Consequences
- Human-readable and self-documenting
- Easy for the agent to parse and write
- No external database dependency
- File can be version-controlled alongside the skill
