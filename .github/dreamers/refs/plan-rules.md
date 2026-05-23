# Plan Naming Rules

Plan filenames MUST be:

- `plan-{slug}.md`

That's it. No `-a`/`-b`/`-c` suffix, no umbrella vs sub-plan distinction. Each plan is independently shippable.

## Slug rules

- lowercase
- replace non-alphanumerics with single hyphen
- trim leading/trailing hyphens
- collapse repeated hyphens
- if empty, use `misc`

## Grouping related plans (optional)

When multiple plans relate to the same feature area, you may share a slug prefix to group them visually:

- `plan-auth-login.md`
- `plan-auth-logout.md`
- `plan-auth-reset.md`

This is purely cosmetic — the slug prefix does not create any semantic relationship between plans. Each plan still stands alone. The user sequences them at invocation time via `/dreamers-full <plan-a> <plan-b> <plan-c>`.

## Location

Plans live in: `./.dreamers/plans/`
