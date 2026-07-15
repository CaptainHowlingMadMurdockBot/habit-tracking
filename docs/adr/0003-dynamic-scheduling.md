# ADR 0003: Dynamic Scheduling via Reply Time

## Status
Accepted

## Context
Users have irregular schedules. A fixed check-in time doesn't work for everyone, especially when sleep patterns are chaotic.

## Decision
The cron job adjusts its fire time based on when the user last replied. When the user engages with the check-in, the agent extracts the reply timestamp, converts it to a cron expression, and updates the cron job. If the user doesn't reply, the schedule stays the same.

## Consequences
- The system adapts to the user's natural rhythm
- No configuration needed from the user
- If the user is silent, the schedule remains stable
- Requires the agent to update the cron job after each reply
