# ADR 0006: Git Worktrees for Dogfooding

## Status
Accepted

## Context
Eman wants to dogfood new improvements on his profile while giving Autumn a stable experience. We needed a way to have two different versions of the skill live simultaneously.

## Decision
Use git worktrees with two branches:
- `main` — tracks development, symlinked to Eman's profile
- `stable` — tracks releases, symlinked to Autumn's profile

To ship a new version to Autumn: merge main into stable and push.

## Consequences
- Eman always runs the latest code
- Autumn only gets tested releases
- One repo, two worktrees, no disk waste
- Symlinks mean no copy step — updates are instant
