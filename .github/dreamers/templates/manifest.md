# Feature: <name>

**Date:** YYYY-MM-DD
**Status:** Draft
**Strategy:** ATOMIC | INCREMENTAL

## Outcome
End-to-end result.

## Plan sequence
| Order | Plan file | Deliverable |
| --- | --- | --- |
| 1 | [plan-01-<name>.md](./plan-01-<name>.md) | <outcome> |

## Shared context
Only cross-plan constraints, decisions, contracts/data shapes, dependencies, and rollback ordering. Each plan must retain enough context to be usable alone.

## End-to-end verification
Outcomes to verify after the whole sequence, with meaningful checks.

Invoke /dreamers with this manifest to preserve order and shared context. Keep it live until all plans ship.
