# ADR 0002: Single Master Cron Job

## Status
Accepted

## Context
Users found it difficult to manage multiple cron jobs for individual habits. Autumn in particular was frustrated that she couldn't remove cron jobs herself.

## Decision
Use a single master cron job that handles all habits. The cron job reads a YAML config file to determine which habits are active. Users add/remove habits conversationally, which updates the YAML file.

## Consequences
- Users never need to touch cron directly
- One cron job to create, one to remove
- Dynamic scheduling is simpler (one schedule to update)
- The YAML file becomes a single source of truth
