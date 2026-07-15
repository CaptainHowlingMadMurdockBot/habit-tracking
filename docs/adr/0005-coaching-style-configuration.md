# ADR 0005: Coaching Style Configuration

## Status
Accepted

## Context
Different users prefer different tones of coaching. Eman prefers direct, non-judgemental language. Autumn may prefer a warmer, more encouraging tone.

## Decision
Make coaching style a configurable option in habits.yaml. Three styles are supported:
- **Direct** — straightforward, no fluff
- **Warm** — encouraging and supportive
- **Minimal** — just the facts

The user chooses during setup and can change at any time.

## Consequences
- Users get the tone that works for them
- Easy to add new styles in the future
- The Coach class is parameterized by style, making it testable
