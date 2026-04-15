# Plan Naming + Numbering Rules

Plan filenames MUST be:
- `plan-{n}-{short-description}.md` — umbrella or standalone plan
- `plan-{n}a-{short-description}.md`, `plan-{n}b-…` — sub-plans

Compute n deterministically:
1) list `plan-*.md` in the target plans directory
2) extract integer between `plan-` and next `-` (ignore trailing letters like `a`, `b`)
3) n = max + 1 (or 1 if none exist)

Slug rules:
- lowercase
- replace non-alphanumerics with single hyphen
- trim leading/trailing hyphens
- collapse repeated hyphens
- if empty, use `misc`

Plans live in: `./.dreamers/plans/`
