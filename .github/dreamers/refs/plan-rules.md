# Plan Naming + Numbering Rules

Plan filenames MUST be:
- `plan-{slug}.md` — umbrella or standalone plan
- `plan-{slug}-a.md`, `plan-{slug}-b.md`, `plan-{slug}-c.md`, … — sub-plans

No numeric prefix. The slug is derived from the feature or task name. Sub-plans append `-a`, `-b`, `-c` in sequence.

Slug rules:
- lowercase
- replace non-alphanumerics with single hyphen
- trim leading/trailing hyphens
- collapse repeated hyphens
- if empty, use `misc`

Plans live in: `./.dreamers/plans/`
