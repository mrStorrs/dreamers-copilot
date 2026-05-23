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

## Feature manifest (optional, for multi-plan work)

When `/dreamers-plan` produces multiple plans AND they share cross-plan context (shared constraints, design decisions, data models, or end-to-end ACs), it may also produce a **feature manifest**:

- `feature-{slug}.md` — lightweight manifest listing the plan sequence + shared context

The manifest is OPTIONAL — produced only when shared context exists. Plans remain independently shippable; the manifest just gives the AI hierarchical context when running the full sequence via `/dreamers-full feature-{slug}.md`.

See `feature-decomposition.md` § "Manifest pattern" for when to use one.

## Location

Plans and manifests live in: `./.dreamers/plans/`
